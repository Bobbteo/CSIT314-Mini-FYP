from database.db_helper import DBHelper


class FRACategory:
    def __init__(self, category_id=None, category_name=None, description=None, status=None, created_at=None):
        self.category_id = category_id
        self.category_name = category_name
        self.description = description
        self.status = status
        self.created_at = created_at

    @staticmethod
    def _row_to_category(row):
        if not row:
            return None

        return FRACategory(
            category_id=row["category_id"],
            category_name=row["category_name"],
            description=row["description"],
            status=row["status"],
            created_at=row["created_at"]
        )

    @staticmethod
    def get_all_categories():
        conn = DBHelper.get_connection()
        rows = conn.execute("""
            SELECT * FROM FRACategory
            ORDER BY category_name ASC
        """).fetchall()
        conn.close()

        return [FRACategory._row_to_category(row) for row in rows]

    @staticmethod
    def find_by_id(category_id):
        conn = DBHelper.get_connection()
        row = conn.execute("""
            SELECT * FROM FRACategory
            WHERE category_id = ?
        """, (category_id,)).fetchone()
        conn.close()

        return FRACategory._row_to_category(row)

    @staticmethod
    def category_exists(category_name, exclude_category_id=None):
        conn = DBHelper.get_connection()

        if exclude_category_id:
            row = conn.execute("""
                SELECT category_id FROM FRACategory
                WHERE category_name = ? AND category_id != ?
            """, (category_name, exclude_category_id)).fetchone()
        else:
            row = conn.execute("""
                SELECT category_id FROM FRACategory
                WHERE category_name = ?
            """, (category_name,)).fetchone()

        conn.close()
        return row is not None

    @staticmethod
    def create_category(category_name, description):
        category_name = category_name.strip()
        description = description.strip()

        if not category_name:
            return {"success": False, "message": "Category name is required."}

        if FRACategory.category_exists(category_name):
            return {"success": False, "message": "Category already exists."}

        conn = DBHelper.get_connection()
        conn.execute("""
            INSERT INTO FRACategory (category_name, description, status)
            VALUES (?, ?, ?)
        """, (category_name, description, "active"))
        conn.commit()
        conn.close()

        return {"success": True, "message": "Category created successfully."}

    @staticmethod
    def update_category(category_id, category_name, description):
        category = FRACategory.find_by_id(category_id)

        if not category:
            return {"success": False, "message": "Category not found."}

        category_name = category_name.strip()
        description = description.strip()

        if not category_name:
            return {"success": False, "message": "Category name is required."}

        if FRACategory.category_exists(category_name, exclude_category_id=category_id):
            return {"success": False, "message": "Category already exists."}

        conn = DBHelper.get_connection()
        conn.execute("""
            UPDATE FRACategory
            SET category_name = ?, description = ?
            WHERE category_id = ?
        """, (category_name, description, category_id))
        conn.commit()
        conn.close()

        return {"success": True, "message": "Category updated successfully."}

    @staticmethod
    def get_active_categories():
        conn = DBHelper.get_connection()
        rows = conn.execute("""
            SELECT * FROM FRACategory
            WHERE status = 'active'
            ORDER BY category_name ASC
        """).fetchall()
        conn.close()

        return [FRACategory._row_to_category(row) for row in rows]
    
    @staticmethod
    def deactivate_category(category_id):
        category = FRACategory.find_by_id(category_id)

        if not category:
            return {"success": False, "message": "Category not found."}

        conn = DBHelper.get_connection()
        conn.execute("""
            UPDATE FRACategory
            SET status = 'inactive'
            WHERE category_id = ?
        """, (category_id,))
        conn.commit()
        conn.close()

        return {"success": True, "message": "Category deactivated successfully."}

    @staticmethod
    def reactivate_category(category_id):
        category = FRACategory.find_by_id(category_id)

        if not category:
            return {"success": False, "message": "Category not found."}

        conn = DBHelper.get_connection()
        conn.execute("""
            UPDATE FRACategory
            SET status = 'active'
            WHERE category_id = ?
        """, (category_id,))
        conn.commit()
        conn.close()

        return {"success": True, "message": "Category reactivated successfully."}