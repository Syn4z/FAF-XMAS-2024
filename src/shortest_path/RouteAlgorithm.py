import numpy as np
from geopy.geocoders import Nominatim
import requests
import json
from sko.GA import GA_TSP
from sko.SA import SA_TSP
import openrouteservice
from openrouteservice import convert
import folium
import dotenv
import os

# Load environment variables
dotenv.load_dotenv()

# api key from openrouteservice
key_api = os.getenv('OPENSTREETMAP_API_KEY')

map_api_init = Nominatim(user_agent="my_app")
client = openrouteservice.Client(key=key_api)

def load_proc(i, i_fin, is_fixed=False):
    proc = i * 100 / i_fin
    int_proc = round(proc, 1)
    if int_proc % 1 == 0 and is_fixed == False:
        print('[' + '=' * int(int_proc) + ' ' * (100 - int(int_proc)) + ']', int(int_proc), '%', end='\r')
        is_fixed = True
    if int_proc % 1 != 0 and is_fixed == True:
        is_fixed = False


# def create_df_by_name(df, route_name):
#     df_route_ = df.loc[df['Route'] == route_name]
#     df_route_ = df_route_.reset_index(drop=True, inplace=False)
#     return df_route_


def save_route(df, location):
    df.to_csv(location)


class RouteAlgorithm(GA_TSP, SA_TSP):

    def __init__(self, df_route_raw, df_route=None, weighted_matrix=None, time_matrix=None, order_list=None, route_name=None):

        self.df_route = df_route
        self.df_route_raw = df_route_raw
        self.weighted_matrix = weighted_matrix
        self.time_matrix = time_matrix
        self.order_list = order_list
        self.df_route_ordered = None
        self.route_name = route_name

    def fit(self):
        df_route_ = self.df_route_raw.loc[self.df_route_raw['Route'] == self.route_name]
        self.df_route = df_route_.reset_index(drop=True, inplace=False)
        return self.df_route

    def create_matrix(self, show_progress=False):
        k = 0
        matrix = []
        for i in range(len(self.df_route)):
            row = []
            for j in range(len(self.df_route)):
                long1 = self.df_route['X Coordinate'][i]
                lat1 = self.df_route['Y Coordinate'][i]
                long2 = self.df_route['X Coordinate'][j]
                lat2 = self.df_route['Y Coordinate'][j]
                r = requests.get(
                    f"http://router.project-osrm.org/route/v1/driving/{lat1},{long1};{lat2},{long2}?overview=false""")
                routes = json.loads(r.content)
                distance = routes.get("routes")[0]["legs"][0]["distance"]
                row.append(distance)
                k += 1

                if show_progress:
                    load_proc(k, len(self.df_route) ** 2)

            matrix.append(row)
        self.weighted_matrix = np.asarray(matrix).astype('float64')
        return self.weighted_matrix

    def create_matrix_ors(self, get_time_matrix=False):

        coords = [[self.df_route['X Coordinate'][indx], self.df_route['Y Coordinate'][indx]][::-1] for indx in
                  range(len(self.df_route))]
        coordinates = coords

        matrix = client.distance_matrix(
            locations=coordinates,
            metrics=['distance', 'duration'],
            validate=False,
        )

        self.weighted_matrix = np.asarray(matrix['distances']).astype('float64')
        self.time_matrix = np.asarray(matrix['durations']).astype('float64')

        if get_time_matrix:
            return self.weighted_matrix, self.time_matrix
        else:
            return self.weighted_matrix

    def find_route_GA(self, view_distance=False):
        num_points = self.weighted_matrix.shape[0]
        distance_matrix = self.weighted_matrix

        def cal_total_distance(routine):
            '''The objective function. input routine, return total distance.
            cal_total_distance(np.arange(num_points))
            '''
            num_points, = routine.shape
            return sum(
                [distance_matrix[routine[i % num_points], routine[(i + 1) % num_points]] for i in range(num_points)])

        ga_tsp = GA_TSP(func=cal_total_distance, n_dim=num_points, size_pop=500, max_iter=500, prob_mut=0.9)
        self.order_list, best_distance = ga_tsp.run()

        if view_distance:
            return self.order_list, best_distance
        else:
            return self.order_list

    def find_route_SA(self, view_distance=False):
        num_points = self.weighted_matrix.shape[0]
        distance_matrix = self.weighted_matrix

        def cal_total_distance(routine):
            '''The objective function. input routine, return total distance.
            cal_total_distance(np.arange(num_points))
            '''
            num_points, = routine.shape
            return sum(
                [distance_matrix[routine[i % num_points], routine[(i + 1) % num_points]] for i in range(num_points)])

        sa_tsp = SA_TSP(func=cal_total_distance, x0=range(num_points), T_max=100, T_min=1, L=10 * num_points)
        self.order_list, best_distance = sa_tsp.run()

        if view_distance:
            return self.order_list, best_distance
        else:
            return self.order_list

    def order_route(self):
        df_route_ordered = self.df_route.reindex(self.order_list)
        self.df_route_ordered = df_route_ordered.reset_index(drop=True, inplace=False)
        return self.df_route_ordered

    def show_route(self, tiles='openstreetmap'):
        coords = tuple([tuple([self.df_route['X Coordinate'][indx], self.df_route['Y Coordinate'][indx]][::-1]) for indx in self.order_list])
        res = client.directions(coords)
        geometry = client.directions(coords)['routes'][0]['geometry']
        decoded = convert.decode_polyline(geometry)

        distance_txt = "<h4> <b>Distance :&nbsp" + "<strong>" + str(
            round(res['routes'][0]['summary']['distance'] / 1000, 1)) + " Km </strong>" + "</h4></b>"
        duration_txt = "<h4> <b>Duration :&nbsp" + "<strong>" + str(
            round(res['routes'][0]['summary']['duration'] / 60, 1)) + " Mins. </strong>" + "</h4></b>"

        m = folium.Map(location=coords[0][::-1], zoom_start=10, control_scale=True, tiles=tiles)
        folium.GeoJson(decoded).add_child(folium.Popup(distance_txt + duration_txt, max_width=300)).add_to(m)

        folium.Marker(
            location=list(coords[0][::-1]),
            icon=folium.Icon(color="green", icon='home'),
        ).add_to(m)

        for place in list(coords)[1:]:
            folium.Marker(
                location=list(place[::-1]),
                icon=folium.Icon(color='darkblue', icon='shopping-cart')
            ).add_to(m)

        folium.Marker(
            location=list(coords[-1][::-1]),
            icon=folium.Icon(color="red", icon='shopping-cart'),
        ).add_to(m)

        return m

    def fit_transform_show(self, show_route=True, view_distance=True):
        self.fit()
        self.create_matrix_ors()
        self.find_route_SA(view_distance=view_distance)

        if show_route:
            return self.show_route()
