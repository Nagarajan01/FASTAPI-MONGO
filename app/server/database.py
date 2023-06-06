import motor.motor_asyncio

from bson.objectid import ObjectId

from decouple import config

MONGO_DETAILS = "mongodb://localhost:27017"

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

database = client.employees

student_collection = database.get_collection("students_collection")

student_address_collection = database.get_collection(
    "students_address_collection")


def student_helper(student) -> dict:
    return {
        "id": str(student["_id"]),
        "fullname": student["fullname"],
        "email": student["email"],
        "course_of_study": student["course_of_study"],
        "year": student["year"],
        "GPA": student["gpa"],
    }


def student_address_helper(student_address) -> dict:
    return {
        "id": str(student_address["_id"]),
        "student_id": str(student_address["pk"]),
        "street_no": student_address["street_no"],
        "city": student_address["city"],
        "state": student_address["state"],
        "country": student_address["country"]
    }
# Retrieve all students present in the database


async def retrieve_students():
    students = []
    async for student in student_collection.find():
        students.append(student_helper(student))
    return students


async def retrieve_students_address():
    students_address = []
    async for student in student_address_collection.find():
        students_address.append(student_address_helper(student))
    return students_address


# Add a new student into to the database
async def add_student(student_data: dict) -> dict:
    student = await student_collection.insert_one(student_data)
    new_student = await student_collection.find_one({"_id": student.inserted_id})
    return student_helper(new_student)


# Retrieve a student with a matching ID
async def retrieve_student(id: str) -> dict:
    student = await student_collection.find_one({"_id": ObjectId(id)})
    if student:
        return student_helper(student)


# Update a student with a matching ID
async def update_student(id: str, data: dict):
    # Return false if an empty request body is sent.
    if len(data) < 1:
        return False
    student = await student_collection.find_one({"_id": ObjectId(id)})
    if student:
        updated_student = await student_collection.update_one(
            {"_id": ObjectId(id)}, {"$set": data}
        )
        if updated_student:
            return True
        return False


# Delete a student from the database
async def delete_student(id: str):
    student = await student_collection.find_one({"_id": ObjectId(id)})
    if student:
        await student_collection.delete_one({"_id": ObjectId(id)})
        return True


async def add_student_address(id: str, data: dict):
    student_id = await student_collection.find_one({"_id": ObjectId(id)})
    new_student = await student_address_collection.count_documents(({"pk": student_id['_id']}))
    if new_student == 0:
        data["pk"] = student_id['_id']
        add_student_address = await student_address_collection.insert_one(data)
        new_student = await student_address_collection.find_one({"_id": add_student_address.inserted_id}, {'_id': 0})
        return new_student
    else:
        return False


async def delete_student_address(id: str):
    student_address = await student_address_collection.find_one({"_id": ObjectId(id)})
    if student_address:
        await student_address_collection.delete_one({"_id": ObjectId(id)})
        return True
