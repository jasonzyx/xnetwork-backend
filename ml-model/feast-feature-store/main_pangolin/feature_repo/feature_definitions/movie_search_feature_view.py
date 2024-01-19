from feast import Entity, FeatureView, ValueType, Field
from feast import FileSource
from feast.types import Float32, String
from datetime import timedelta

# Define an entity for the user
user_entity = Entity(name="userId", value_type=ValueType.INT64, description="User ID")
movie_entity = Entity(name="movieId", value_type=ValueType.INT64, description="Movie ID")

# Define the FileSource for user_stats
user_stats_source = FileSource(
    path="./data/user_stats.parquet",
    event_timestamp_column="event_timestamp"
)

# Define the FileSource for movies
movies_source = FileSource(
    path="./data/movies.parquet",
    event_timestamp_column="event_timestamp"
)

# Define your FeatureViews
user_stats_view = FeatureView(
    name="user_stats_view",
    entities=[user_entity],
    ttl=timedelta(days=1),
    schema=[
        Field(name="avg_rating", dtype=Float32),
        Field(name="rating_stddev", dtype=Float32)
    ],
    source=user_stats_source
)

movies_view = FeatureView(
    name="movies_view",
    entities=[movie_entity],
    ttl=timedelta(days=1),
    schema=[
        Field(name="title", dtype=String),
        Field(name="image", dtype=String),
        Field(name="genres", dtype=String)
    ],
    source=movies_source
)