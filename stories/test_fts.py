import sqlite3

# Connect to the database (creates a new one if it doesn't exist)
conn = sqlite3.connect('example.db')
cursor = conn.cursor()

# Create a table and enable FTS5 for full-text search
cursor.execute('''CREATE VIRTUAL TABLE documents USING fts5(title, content, tokenize="unicode61")''')

# Insert some sample datac
id = 1
cursor.execute("INSERT INTO documents (rowid, title, content) VALUES (?, ?, ?)", 
               (id, "# Python Tutorial", "This *is* _a_  > tutorial about Python programming."))

# cursor.execute("INSERT INTO documents VALUES (?, ?, ?);", ("SQLite Basics", "Learn the basics of SQLite database."))
# cursor.execute("INSERT INTO documents VALUES (?, ?, ?)", ["Data Science with Python", "Explore data science concepts using Python."])

# Commit the changes
conn.commit()

# Perform a full-text search
search_term = "python"
cursor.execute("SELECT * FROM documents WHERE documents MATCH ?", (search_term,))
results = cursor.fetchall()

# Print the results
for row in results:
    print(row)

# Close the connection
conn.close()