from dotenv import load_dotenv
import os
import sqlite3
import psycopg2
# import MySQLdb

"""
pg_dump -h localhost -p 5432 -U niall -d dpcdb | psql -h 0.0.0.0 -p 5555 -U niall -d dpcdb
"""

from playhouse.postgres_ext import *

load_dotenv()

database = PostgresqlDatabase(
    database=os.getenv("POSTGRES_DATABASE"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    host=os.getenv("POSTGRES_HOST"),
    port=int(os.getenv("POSTGRES_PORT")),
    autorollback=True,
)


# database = SqliteDatabase("dpc.sqlite.db", autorollback=True)

class BaseModel(Model):
    class Meta:
        database = database

    repr_keys = []

    def __repr__(self):
        values = []

        for key in self.repr_keys:
            value = getattr(self, key)
            if isinstance(value, str):
                value = f'"{value}"'

            values.append("{}={}".format(key, value))

        return f"<{self.__class__.__name__} {' '.join(values)}>"


class Member(BaseModel):
    id = IntegerField(null=False, index=True, unique=True)

    name = CharField(null=False, index=True)
    join_date = DateField(null=False, index=False)

    repr_keys = ["name", "join_date"]

    class Meta:
        db_table = "members"

        order_by = ("name",)


class Challenge(BaseModel):
    id = IntegerField(null=False, index=True, unique=True)

    name = CharField(null=False, index=True, unique=True)
    description = TextField()

    submission_start = DateField()
    submission_end = DateField()

    voting_start = DateField()
    voting_end = DateField()

    num_submissions = IntegerField()
    num_disqualifications = IntegerField()

    num_votes = IntegerField()
    num_comments = IntegerField()

    average_score = DoubleField()
    highest_score = DoubleField()
    median_score = DoubleField()
    lowest_score = DoubleField()

    repr_keys = ["name", "description"]

    class Meta:
        db_table = "challenges"

        order_by = (
            "voting_start",
            "name",
        )


class Image(BaseModel):
    id = IntegerField(null=False, index=True, unique=True)

    challenge = ForeignKeyField(
        Challenge, related_name="images", on_delete="CASCADE", null=False, index=True
    )
    photographer = ForeignKeyField(
        Member, related_name="images", on_delete="CASCADE", null=False, index=True
    )

    name = CharField(null=False)

    votes = ArrayField(IntegerField, null=False)

    average_all = DoubleField(null=True)
    average_comments = DoubleField(null=True)
    average_participants = DoubleField(null=True)
    average_non_participants = DoubleField(null=True)

    num_views = IntegerField(null=True)
    num_votes = IntegerField(null=True)

    disqualified = BooleanField(null=False)

    repr_keys = ["name", "average_all"]

    class Meta:
        db_table = "images"

        order_by = ("challenge", "-average_all")

        # indexes = (
        #     (('challenge', 'photographer'), True),
        # )


class Comment(BaseModel):
    id = IntegerField(null=False, index=True, unique=True)

    commenter = ForeignKeyField(
        Member, related_name="comments", on_delete="CASCADE", null=False, index=True
    )

    image = ForeignKeyField(
        Image, related_name="comments", on_delete="CASCADE", null=False, index=True
    )

    raw_comment = TextField()
    comment = TextField()

    date = DateTimeField()
    edited = DateTimeField(null=True)

    has_quote = BooleanField()
    made_during_challenge = BooleanField()

    repr_keys = ["image", "commenter", "comment"]

    class Meta:
        db_table = "comments"

        order_by = ("image", "date")

        # indexes = (
        #     (('image', 'commenter', 'date'), True),
        # )


class Bling(BaseModel):
    id = PrimaryKeyField()

    awarder = ForeignKeyField(
        Member, related_name="bling", on_delete="CASCADE", null=False, index=True
    )

    name = CharField(index=True)
    slug = CharField(index=True)

    description = TextField()

    img_src = CharField()

    regex = ArrayField(CharField)

    repr_keys = ["awarder", "name"]

    class Meta:
        db_name = "bling"

        order_by = ("awarder", "name")

        indexes = ((("awarder", "name"), True),)


class Awards(BaseModel):
    id = PrimaryKeyField()

    bling = ForeignKeyField(
        Bling, related_name="awards", on_delete="CASCADE", null=False, index=True
    )

    user = ForeignKeyField(
        Member, related_name="awards", on_delete="CASCADE", null=False, index=True
    )

    comment = ForeignKeyField(
        Comment, related_name="awards", on_delete="CASCADE", null=False, index=True
    )

    image = ForeignKeyField(
        Image, related_name="awards", on_delete="CASCADE", null=False, index=True
    )

    challenge = ForeignKeyField(
        Challenge, related_name="awards", on_delete="CASCADE", null=False, index=True
    )

    repr_keys = ["bling", "comment"]

    # @property
    # def challenge(self):
    #     return self.image.challenge
    #
    # @property
    # def awarder(self):
    #     return self.bling.member
    #
    # @property
    # def recipient(self):
    #     return self.image.photographer

    class Meta:
        db_name = "awards"

        order_by = ("comment", "bling")

        indexes = ((("bling", "comment"), True),)


tables = [
    Member,
    Challenge,
    Image,
    Comment,
    Bling,
    Awards,
]

database.create_tables(models=tables, safe=True)
