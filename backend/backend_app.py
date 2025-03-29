from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)
CORS(app) # This will enable CORS for all routes

# Swagger configuration
SWAGGER_URL = "/api/docs"   # swagger endpoint e.g. HTTP://localhost:5002/api/docs
API_URL = "/static/masterblog.json"

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'Masterblog API'
    }
)

app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

 # Sample data (stored in memory)
POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
    {"id": 3, "title": "Third post", "content": "This is the third post."},
]

# Auto-increment ID generator
def get_next_id():
    if not POSTS:
        return 1
    return max(post["id"] for post in POSTS) + 1

@app.route("/")
def home():
    return "Welcome to Masterblog API! Visit /api/posts to see blog posts."

# GET: Fetch all blog posts with optional sorting
@app.route('/api/posts', methods=['GET'])
def get_posts():
    sort_by = request.args.get("sort")
    direction = request.args.get("direction", "asc")

    # Validate sort field and direction
    if sort_by and sort_by not in ["title", "content"]:
        return jsonify({"error": "Invalid sort field. Use 'title' or 'content'."}), 400
    if direction not in ["asc", "desc"]:
        return jsonify({"error": "Invalid direction. Use 'asc' or 'desc'."}), 400

    # Sort a copy of the posts (without modifying the original list)
    sorted_posts = sorted(POSTS, key=lambda post: post[sort_by].lower(), reverse=(direction == "desc")) if sort_by else POSTS

    return jsonify(sorted_posts)

# POST: Add a new blog post
@app.route('/api/posts', methods=['POST'])
def add_post():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Invalid JSON. Please send a valid JSON body."}), 400

        title = data.get("title")
        content = data.get("content")

        if not title or not content:
            return jsonify({"error": "Title and content are required"}), 400

        new_post = {"id": get_next_id(), "title": title, "content": content}
        POSTS.append(new_post)

        return jsonify(new_post), 201  # 201 Created status code

    except Exception as e:
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500

# DELETE: Delete a blog post by ID
@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    global POSTS
    post_to_delete = next((post for post in POSTS if post["id"] == post_id), None)

    if not post_to_delete:
        return jsonify({"error": f"Post with ID {post_id} not found"}), 404

    # Remove the post from the list
    POSTS = [post for post in POSTS if post["id"] != post_id]
    return jsonify({"message": f"Post with ID {post_id} has been deleted successfully."}), 200

# PUT: Update a blog post by ID
@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    data = request.get_json()

    # Ensure the request data is a dictionary
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid request format. Expected a JSON object."}), 400

    post = next((post for post in POSTS if post["id"] == post_id), None)

    if not post:
        return jsonify({"error": f"Post with ID {post_id} not found"}), 404

    # Update the title and content if provided
    post["title"] = data.get("title", post["title"])
    post["content"] = data.get("content", post["content"])
    return jsonify(post), 200

# GET: Search for posts (by title or content)
@app.route('/api/posts/search', methods=['GET'])
def search_post():
    title_query = request.args.get("title", "").strip().lower()
    content_query = request.args.get("content", "").strip().lower()

    # Check if at least one search parameter is provided
    if not title_query and not content_query:
        return jsonify({"error": "Please provide a search query (title or content)."}), 400

    filtered_posts = [
        post for post in POSTS
        if (title_query and title_query in post["title"].lower()) or
           (content_query and content_query in post["content"].lower())
    ]
    if not filtered_posts:
        return jsonify({"message": "No matching posts found."}), 404

    return jsonify(filtered_posts), 200

    # Run the Flask server
if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5002, debug=True)