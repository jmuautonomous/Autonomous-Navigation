#!/usr/bin/env python

import sys
import tf
import rospy

#This class still needs testing

from geometry_msgs.msg import Pose, Point #point iis able to be used for path planning in a 3d space
from sensor_msgs.msg import NavSatFix #standard ros message for GPS data

#current anchor is the center of the xlabs building, with direction pointing directly north
anchor_lat = 38.431960
anchor_long = -78.875910
anchor_elev = 396 #meters above sea level
anchor_theta = 0 #angle pointing directly north
earth_radius = 6371000 #meters 
    
def get_point(current_gps):
    relative_point = Point()
    current_lat = current_gps.latitude
    current_long = current_gps.longitude
    if current_gps.altitude == NaN: #If an altitude is not provided
        result = xy_between_points(anchor_lat, anchor_long, anchor_theta, current_lat, current_long)
        relative_point.x = result[0]
        relative_point.y = result[1]
        relative_point.z = anchor_elev #elevation is assumed to be the same as the start if no elevation is provided
    else: #If an altitude is provided
        current_elev = current_gps.altitude
        result = xyz_between_points(anchor_lat, anchor_long, anchor_elev, anchor_theta, current_lat, current_long, current_elev)
        relative_point.x = result[0]
        relative_point.y = result[1]
        relative_point.z = result[2]
    return relative_point

def distance_between_points(lat1, lng1, lat2, lng2):
    """
    :return: distance (meters) between two points. This is approximate as the math assumes the earth is a sphere

    https://www.movable-type.co.uk/scripts/latlong.html
    uses meters for earth radius
    """
    global earth_radius
    lat1 = math.radians(lat1)
    lng1 = math.radians(lng1)
    lat2 = math.radians(lat2)
    lng2 = math.radians(lng2)

    a = math.sin((lat2-lat1)/2)*math.sin((lat2-lat1)/2) + math.cos(lat1) * math.cos(lat2) * math.sin((lng2-lng1)/2)*math.sin((lng2-lng1)/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt((1-a)))
    distance = earth_radius * c
    return distance
    
def xyz_to_lat_long(point):
    """
    :return: lat-long based on a single point in meters (0,0,0 represents xlabs)
    """
    global anchor_lat, anchor_long, earth_radius	
    x = point.x
    y = point.y
    lat1 = math.radians(anchor_lat)
    lng1 = math.radians(anchor_long)
    bearing = math.atan2(x, y)
    distance = math.sqrt(x*x + y*y)
    angular_dist = distance/earth_radius
    lat2 = math.asin(math.sin(lat1) * math.cos(angular_dist) + math.cos(lat1) * math.sin (angular_dist) * math.cos(bearing))
    lng2 = lng1 + math.atan2( math.sin(bearing) * math.sin(angular_dist) * math.cos(lat1),
	    math.cos(angular_dist) - math.sin(lat1) * math.sin(lat2))
    
    return (lat2, lng2)

def direction_between_points(lat1, lng1, lat2, lng2):
    """
    :return: bearing between two points (degrees)
    This calculates for the bearing between two points.
    """
    lat1 = math.radians(lat1)
    lng1 = math.radians(lng1)
    lat2 = math.radians(lat2)
    lng2 = math.radians(lng2)

    bearing = math.atan2((math.sin(lng2-lng1)*math.cos(lat2)),(math.cos(lat1)*math.sin(lat2)-math.sin(lat1)*math.cos(lat2)*math.cos(lng2-lng1)))
    bearing = (math.degrees(bearing)+360)%360
    return bearing
def xyz_between_points(lat1, lng1, elev1, theta1, lat2, lng2, elev2):
    """
    This is incomplete, math could be innaccurate at doing elevation.
    """
    distance_flat = distance_between_points(lat1,lng1,lat2,lng2)
    angle = math.radians( (theta1+direction_between_points(lat1,lng1,lat2,lng2)) % 360 )
    forward = math.cos(angle)*distance_flat
    sideways = math.sin(angle)*distance_flat
    verticle = elev2-elev1
    return (forward, sideways, verticle)
def xy_between_points(lat1, lng1, theta1, lat2, lng2):
    distance_flat = distance_between_points(lat1,lng1,lat2,lng2)
    angle = math.radians( (theta1+direction_between_points(lat1,lng1,lat2,lng2)) % 360 )
    forward = math.cos(angle)*distance_flat
    sideways = math.sin(angle)*distance_flat
    return (forward, sideways)