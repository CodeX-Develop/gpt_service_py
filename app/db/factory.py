from abc import ABC, abstractmethod
from enum import Enum
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

import psycopg2
from psycopg2 import sql

class DBType(Enum):
    POSTGRES = 'postgres'
    MONGODB = 'mongodb'
    SQLITE = 'sqlite'
    # Puedes agregar más según tus necesidades


class DatabaseFactory(ABC):
    @abstractmethod
    def create(self, data):
        pass
    @abstractmethod
    def read(self, id):
        pass
    @abstractmethod
    def update(self, id, data):
        pass
    @abstractmethod
    def delete(self, id):
        pass


class PostgresFactory(DatabaseFactory):
    
    def __init__(self, connection):
        self.connection = psycopg2.connect(**connection)
        self.cursor = self.connection.cursor()

    def create(self, data, table):
        self.create_table_if_not_exists(table)
        keys = data.keys()
        values = [sql.Identifier(i) for i in data.values()]
        insert = sql.SQL("INSERT INTO {} ({}) VALUES ({}) RETURNING id").format(
            sql.Identifier(table),
            sql.SQL(',').join(map(sql.Identifier, keys)),
            sql.SQL(',').join(values)
        )
        self.cursor.execute(insert)
        self.connection.commit()
        return self.cursor.fetchone()[0]

    def read(self, id, table):
        self.create_table_if_not_exists(table)
        select = sql.SQL("SELECT * FROM {} WHERE id = {}").format(
            sql.Identifier(table),
            sql.Identifier(str(id))
        )
        self.cursor.execute(select)
        return self.cursor.fetchone()

    def update(self, id, data, table):
        self.create_table_if_not_exists(table)
        keys_and_values = [f"{key} = {value}" for key, value in data.items()]
        update = sql.SQL("UPDATE {} SET {} WHERE id = {}").format(
            sql.Identifier(table),
            sql.SQL(',').join(sql.SQL(i) for i in keys_and_values),
            sql.Identifier(str(id))
        )
        self.cursor.execute(update)
        self.connection.commit()
        return self.cursor.rowcount

    def delete(self, id, table):
        self.create_table_if_not_exists(table)
        delete = sql.SQL("DELETE FROM {} WHERE id = {}").format(
            sql.Identifier(table),
            sql.Identifier(str(id))
        )
        self.cursor.execute(delete)
        self.connection.commit()
        return self.cursor.rowcount
    
    def create_table_if_not_exists(self, table):
        schema = ["id serial PRIMARY KEY", "user varchar", "prompt varchar", "chat_id foreign key"]
        create_table = sql.SQL("CREATE TABLE IF NOT EXISTS {} ({})").format(
            sql.Identifier(table),
            sql.SQL(',').join(sql.SQL(i) for i in schema)
        )
        self.cursor.execute(create_table)
        self.connection.commit()

class MongoDBFactory(DatabaseFactory):

    def __init__(self, connection):
        self.client = AsyncIOMotorClient(connection)
        self.db = self.client["test_db"] 

    async def check_connection(self):
        try:
            await self.client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print(e)

    async def create(self, data, collection):
        result = await self.db[collection].insert_one(data)
        return str(result.inserted_id)
    
    async def read(self, id, collection):
        result = await self.db[collection].find_one({"_id": ObjectId(id)})
        return result
    
    async def read_one(self, query, collection):
        result = await self.db[collection].find_one(query)
        return result
    
    async def read_all(self, query, collection):
        result = []
        async for document in self.db[collection].find(query):
            result.append(document)
        return result

    async def update(self, id, data, collection):
        result = await self.db[collection].update_one({"_id": ObjectId(id)}, {"$set": data})
        return result.modified_count
    
    async def update_one(self, query, data, collection):
        result = await self.db[collection].update_one(query, {"$set": data})
        return result.modified_count

    async def delete(self, id, collection):
        result = await self.db[collection].delete_one({"_id": ObjectId(id)})
        return result.deleted_count
    
    async def delete_one(self, query, collection):
        result = await self.db[collection].delete_one(query)
        return result.deleted_count


# Puedes agregar más clases similares para MongoDB, SQLite, etc.


def get_database_factory(db_type: DBType, connection):
    if db_type == DBType.POSTGRES:
        return PostgresFactory(connection)
    elif db_type == DBType.MONGODB:
        return MongoDBFactory(connection)
    elif db_type == DBType.SQLITE:
        # return SQLiteFactory(connection)
        pass
    # Agrega más opciones según tus necesidades

    raise ValueError(f"No se encontró una factory para el tipo de base de datos {db_type}")