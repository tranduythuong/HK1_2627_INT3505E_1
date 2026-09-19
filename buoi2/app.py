from flask import Flask, json, jsonify, request, make_response
import sqlite3
import hashlib

app = Flask(__name__)

DATABASE = "books.db"

DEFAULT_SIZE = 10
MAX_SIZE = 20


# =========================================================
# DATABASE
# =========================================================

def get_db():
    conn = sqlite3.connect(DATABASE)

    # Cho phép truy cập dữ liệu bằng tên cột:
    # book["id"], book["title"], book["author"]
    conn.row_factory = sqlite3.Row

    return conn


# =========================================================
# CREATE - POST /books
# =========================================================

@app.route('/books', methods=['POST'])
def create_book():

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            'error': 'Expected JSON'
        }), 415

    title = data.get('title')
    author = data.get('author')

    if not title or not author:
        return jsonify({
            'error': 'Missing title or author'
        }), 422

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO books (title, author)
        VALUES (?, ?)
    """, (title, author))

    conn.commit()

    # Lấy ID vừa được SQLite tạo
    book_id = cursor.lastrowid

    cursor.execute("""
        SELECT id, title, author
        FROM books
        WHERE id = ?
    """, (book_id,))

    book = cursor.fetchone()

    conn.close()

    book = dict(book)

    response = make_response(
        jsonify(book),
        201
    )

    response.headers['Location'] = f'/books/{book["id"]}'

    return response


# =========================================================
# GET - GET /books
# =========================================================

@app.route('/books', methods=['GET'])
def get_books():

    # -----------------------------------------------------
    # PAGINATION
    # -----------------------------------------------------

    page = request.args.get(
        'page',
        default=1,
        type=int
    )

    size = request.args.get(
        'size',
        default=DEFAULT_SIZE,
        type=int
    )

    if page is None or size is None:
        return jsonify({
            'error': 'Invalid page or size'
        }), 400

    page = max(page, 1)
    size = max(min(size, MAX_SIZE), 1)

    # -----------------------------------------------------
    # FILTERING
    # -----------------------------------------------------

    author = request.args.get(
        'author',
        default='',
        type=str
    )

    title = request.args.get(
        'title',
        default='',
        type=str
    )

    conn = get_db()
    cursor = conn.cursor()

    # -----------------------------------------------------
    # BUILD SQL
    # -----------------------------------------------------

    sql = """
        SELECT id, title, author
        FROM books
        WHERE 1 = 1
    """

    params = []

    # Filter author
    if author:
        sql += """
            AND LOWER(author) = LOWER(?)
        """
        params.append(author)

    # Filter title
    if title:
        sql += """
            AND LOWER(title) = LOWER(?)
        """
        params.append(title)

    # -----------------------------------------------------
    # COUNT TOTAL
    # -----------------------------------------------------

    count_sql = """
        SELECT COUNT(*)
        FROM books
        WHERE 1 = 1
    """

    count_params = []

    if author:
        count_sql += """
            AND LOWER(author) = LOWER(?)
        """
        count_params.append(author)

    if title:
        count_sql += """
            AND LOWER(title) = LOWER(?)
        """
        count_params.append(title)

    cursor.execute(
        count_sql,
        count_params
    )

    total = cursor.fetchone()[0]

    # -----------------------------------------------------
    # PAGINATION
    # -----------------------------------------------------

    start = (page - 1) * size

    sql += """
        LIMIT ? OFFSET ?
    """

    params.append(size)
    params.append(start)

    cursor.execute(sql, params)

    rows = cursor.fetchall()

    conn.close()

    # sqlite3.Row -> dict
    items = []

    for row in rows:
        items.append(dict(row))

    # -----------------------------------------------------
    # TOTAL PAGES
    # -----------------------------------------------------

    total_pages = (total + size - 1) // size

    # -----------------------------------------------------
    # HATEOAS
    # -----------------------------------------------------

    def make_url(page_number):

        url = f"/books?page={page_number}&size={size}"

        if author:
            url += f"&author={author}"

        if title:
            url += f"&title={title}"

        return url

    links = {
        'self': {
            'href': make_url(page)
        },
        'first': {
            'href': make_url(1)
        },
        'last': {
            'href': make_url(max(total_pages, 1))
        }
    }

    if page > 1:
        links['prev'] = {
            'href': make_url(page - 1)
        }

    if page < total_pages:
        links['next'] = {
            'href': make_url(page + 1)
        }

    # -----------------------------------------------------
    # RESPONSE
    # -----------------------------------------------------

    body = {
        'list': items,

        'pagination': {
            'page': page,
            'size': size,
            'total': total,
            'total_pages': total_pages
        },

        'links': links
    }

    response = make_response(
        jsonify(body),
        200
    )

    response.headers['Cache-Control'] = 'public, max-age=30'

    return response


# =========================================================
# GET ONE - GET /books/<book_id>
# =========================================================

@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title, author
        FROM books
        WHERE id = ?
    """, (book_id,))

    book = cursor.fetchone()

    conn.close()

    # 1. Kiểm tra book có tồn tại không
    if book is None:
        return jsonify({
            'error': 'Book not found'
        }), 404

    # 2. Chuyển Row -> dictionary
    book_dict = dict(book)

    # 3. Tạo chuỗi JSON để tạo ETag
    book_json = json.dumps(
        book_dict,
        sort_keys=True
    )

    # 4. Tạo ETag
    etag = hashlib.md5(
        book_json.encode()
    ).hexdigest()

    # Thêm dấu " vào ETag
    etag = f'"{etag}"'

    # 5. Lấy If-None-Match từ request
    client_etag = request.headers.get("If-None-Match")

    # 6. So sánh
    if client_etag == etag:
        return '', 304

    # 7. Nếu khác → trả dữ liệu
    res = make_response(
        jsonify({
            'status': 'success',
            'book': book_dict
        }),
        200
    )

    # 8. Gửi ETag cho client
    res.headers["ETag"] = etag

    return res


# =========================================================
# PATCH - PATCH /books/<book_id>
# =========================================================

@app.route('/books/<int:book_id>', methods=['PATCH'])
def patch_book(book_id):

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            'error': 'Expected JSON'
        }), 415

    title = data.get('title')
    author = data.get('author')

    conn = get_db()
    cursor = conn.cursor()

    # Kiểm tra book có tồn tại không
    cursor.execute("""
        SELECT id, title, author
        FROM books
        WHERE id = ?
    """, (book_id,))

    book = cursor.fetchone()

    if book is None:
        conn.close()

        return jsonify({
            'error': 'Book not found'
        }), 404

    # -----------------------------------------------------
    # UPDATE
    # -----------------------------------------------------

    if 'title' in data:
        cursor.execute("""
            UPDATE books
            SET title = ?
            WHERE id = ?
        """, (title, book_id))

    if 'author' in data:
        cursor.execute("""
            UPDATE books
            SET author = ?
            WHERE id = ?
        """, (author, book_id))

    conn.commit()

    # Lấy lại dữ liệu sau khi update
    cursor.execute("""
        SELECT id, title, author
        FROM books
        WHERE id = ?
    """, (book_id,))

    updated_book = cursor.fetchone()

    conn.close()

    return jsonify({
        'status': 'success',
        'book': dict(updated_book)
    }), 200


# =========================================================
# PUT - PUT /books/<book_id>
# =========================================================

@app.route('/books/<int:book_id>', methods=['PUT'])
def put_book(book_id):

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            'error': 'Expected JSON'
        }), 415

    title = data.get('title')
    author = data.get('author')

    if not title or not author:
        return jsonify({
            'error': 'Missing title or author'
        }), 422

    conn = get_db()
    cursor = conn.cursor()

    # Kiểm tra tồn tại
    cursor.execute("""
        SELECT id
        FROM books
        WHERE id = ?
    """, (book_id,))

    book = cursor.fetchone()

    if book is None:
        conn.close()

        return jsonify({
            'error': 'Book not found'
        }), 404

    # PUT thay thế toàn bộ resource
    cursor.execute("""
        UPDATE books
        SET title = ?,
            author = ?
        WHERE id = ?
    """, (title, author, book_id))

    conn.commit()

    # Lấy lại book
    cursor.execute("""
        SELECT id, title, author
        FROM books
        WHERE id = ?
    """, (book_id,))

    updated_book = cursor.fetchone()

    conn.close()

    return jsonify({
        'status': 'success',
        'book': dict(updated_book)
    }), 200


# =========================================================
# DELETE - DELETE /books/<book_id>
# =========================================================

@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):

    conn = get_db()
    cursor = conn.cursor()

    # Kiểm tra book tồn tại
    cursor.execute("""
        SELECT id
        FROM books
        WHERE id = ?
    """, (book_id,))

    book = cursor.fetchone()

    if book is None:
        conn.close()

        return jsonify({
            'error': 'Book not found'
        }), 404

    # DELETE
    cursor.execute("""
        DELETE FROM books
        WHERE id = ?
    """, (book_id,))

    conn.commit()
    conn.close()

    return '', 204


# =========================================================
# RUN SERVER
# =========================================================

if __name__ == '__main__':
    app.run(
        host='localhost',
        port=4040,
        debug=True
    )