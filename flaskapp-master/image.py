
import base64
from PIL import Image
import io
import mysql.connector


mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password='root',
    database="itl"  # Name of the database
)

# Create a cursor object
cursor = mydb.cursor()

# Prepare the query
query = 'SELECT cover FROM book WHERE book_id=26'

# Execute the query to get the file
cursor.execute(query)

data = cursor.fetchall()

# The returned data will be a list of list
image = data[0]

# Decode the string
binary_data = base64.b64decode(image[0])

# Convert the bytes into a PIL image
image = Image.open( io.BytesIO(binary_data))
im=Image.save(image)
# Display the image

