from fastapi import FastAPI,  Body
from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List, Optional
from pydantic import BaseModel
import numpy as np
import pandas as pd
from gensim.models import Word2Vec
from sklearn.metrics.pairwise import cosine_similarity
from ...core.db.database import get_db_client
from sklearn.metrics.pairwise import cosine_similarity




all_interests = ["Self-care",
      "Spa",
      "Meditation",
      "Gym",
      "Yoga",
      "Hot yoga",
      "Wellness retreats",
      "Minimalism",
      "Sustainable living",
      "Gardening",
      "Home decor",
      "Fashion",
      "Beauty",
      "Aromatherapy",
      "Personal development",
      "Harry Potter",
      "Netflix",
      "Theatre",
      "Spotify",
      "SoundCloud",
      "Live music",
      "Stand-up comedy",
      "Video games",
      "Board games",
      "Anime",
      "Comic books",
      "Book club",
      "Movie nights",
      "Karaoke",
      "Dance parties",
      "Hiking",
      "Camping",
      "Fishing",
      "Canoeing",
      "Surfing",
      "Mountain biking",
      "Rock climbing",
      "Bird watching",
      "Photography",
      "Geocaching",
      "Skiing",
      "Snowboarding",
      "Kite surfing",
      "Paragliding",
      "Horseback riding",
      "Sushi",
      "Coffee",
      "Craft beer",
      "Gin & tonic",
      "Foodie tour",
      "Vegan cuisine",
      "Wine tasting",
      "Baking",
      "Cooking classes",
      "Farmers markets",
      "Mixology",
      "Ethnic cuisines",
      "Cheese tasting",
      "Chocolate making",
      "Barbecue",
      "Social development",
      "Freelance",
      "Start-ups",
      "Digital Marketing",
      "Networking events",
      "Entrepreneurship",
      "Professional development",
      "Tech meetups",
      "Creative writing",
      "Investing",
      "Public speaking",
      "Mentorship",
      "Leadership workshops",
      "Coding bootcamps",
      "Business analytics",
      "Football",
      "Basketball",
      "Hockey",
      "Cricket",
      "Tennis",
      "Golf",
      "Running",
      "Cycling",
      "Swimming",
      "Martial arts",
      "Yoga sports",
      "Gymnastics",
      "Archery",
      "Pilates",
      "Bowling",
      "Gadgets",
      "Programming",
      "Web development",
      "AI and robotics",
      "Cybersecurity",
      "Gaming",
      "Virtual reality",
      "Drones",
      "Tech DIY",
      "Smart home technology",
      "Data science",
      "Machine learning",
      "Blockchain",
      "E-sports",
      "Mobile app development",
      "Museums",
      "Painting",
      "Sculpture",
      "Photography",
      "Dance",
      "Opera",
      "Symphony",
      "Ballet",
      "Film making",
      "Creative arts",
      "Literature",
      "Fashion design",
      "Theater production",
      "Art history",
      "Pottery",
      "Road trips",
      "Backpacking",
      "Cruise vacations",
      "Adventure travel",
      "Historical travel",
      "Luxury travel",
      "Eco-tourism",
      "Volunteer travel",
      "Cultural exchange",
      "Language learning",
      "City tours",
      "Wildlife safaris",
      "Scuba diving",
      "Mountaineering",
      "Festival hopping",
      "DIY",
      "Upcycling",
      "Vintage clothing",
      "Vintage fashion",
      "Voguing",
      "Pet care",
      "Astrology",
      "Board games",
      "Magic and illusions",
      "Podcasting",
      "Origami",
      "Gardening",
      "Knitting",
      "Home brewing",
      "Aquascaping"]

model = Word2Vec([all_interests], min_count=1, vector_size=100, window=1, seed=42, epochs=100)

def average_vector(interests):
    vectors = [model.wv[word] for word in interests if word in model.wv]
    if vectors:
        normalized_vectors = np.array([vector / np.linalg.norm(vector) for vector in vectors])
        return np.mean(normalized_vectors, axis=0)
    else:
        return np.zeros(model.vector_size)
    


def get_vibescore(current_user_id, user_avg_vector, dict_users_vectors):
    similarity_scores = {}
    for comp_user_id, comp_user_avg_vector in dict_users_vectors.items():
        if comp_user_id != current_user_id:
            similarity_scores[comp_user_id] = cosine_similarity([user_avg_vector], [comp_user_avg_vector])[0][0]

    sorted_users = sorted(similarity_scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_users

