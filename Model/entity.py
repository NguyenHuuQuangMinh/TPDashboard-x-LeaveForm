from config import engine
from sqlalchemy import text
class Entity:
    @staticmethod
    def get_nts(code=None, name=None, category=None, tradeshow=None, page=1,per_page=100):
        filters = []
        params = {}

        if code:
            filters.append("code ILIKE :code")
            params["code"] = f"%{code}%"

        if name:
            filters.append("name ILIKE :name")
            params["name"] = f"%{name}%"

        if category:
            categories = [c.strip() for c in category.split(",")]
            filters.append("category = ANY(:category)")
            params["category"] = categories

        if tradeshow:
            filters.append("message_text = ANY(:tradeshow)")
            params["tradeshow"] = f"%{tradeshow}%"

        where_clause = ""

        if filters:
            where_clause ="WHERE " + " AND ".join(filters)

        offset = (page - 1) * per_page

        params['offset'] = offset
        params['limit'] = per_page

        count_query = text(f"""
            SELECT COUNT(*)
            FROM drm_nts_messages
            {where_clause}
        """)

        data_query = text(f"""
                    SELECT
                        code,
                        name,
                        category,
                        message_text,
                        created_date
                    FROM drm_nts_messages
                    {where_clause}
                    ORDER BY created_date DESC
                    LIMIT :limit OFFSET :offset
                """)
        with engine.connect() as conn:
            total = conn.execute(count_query, params).scalar()
            message = conn.execute(data_query, params).mappings().all()
        return total, message

    @staticmethod
    def get_cate():
        category_query = text("""
                            SELECT DISTINCT category
                            FROM drm_nts_messages
                            ORDER BY category
                        """)
        with engine.connect() as conn:
            result = conn.execute(category_query).scalars().all()
        return result

    @staticmethod
    def get_details(code):
        params = {}
        where_clause = ""
        if code:
            where_clause = "WHERE agent_code = :code"
            params["code"] = code

        contact_sql = text(f"""
                  SELECT DISTINCT contact_name, title, email, phone
                  FROM drm_info
                  {where_clause}
              """)

        # Revenue by year/month — chỉ từ 2025 trở đi
        yearly_sql = text(f"""
                  SELECT
                      EXTRACT(YEAR FROM last_service_date)::int  AS year,
                      EXTRACT(MONTH FROM last_service_date)::int AS month,
                      SUM(profit) AS profit
                  FROM "View_Revenue_By_Agent"
                    {where_clause}
                    {"AND" if where_clause else "WHERE"}
                    EXTRACT(YEAR FROM last_service_date) >= 2025
                  GROUP BY
                      EXTRACT(YEAR FROM last_service_date),
                      EXTRACT(MONTH FROM last_service_date)
                  ORDER BY year, month
              """)
        with engine.connect() as conn:
            contacts = conn.execute(contact_sql, params).mappings().all()
            yearly = conn.execute(yearly_sql, params).mappings().all()
        return contacts, yearly

    @staticmethod
    def get_nts_detail():
        query = text(f"""
                    SELECT DISTINCT note_category, description
                    FROM nts_cate
                """)
        with engine.connect() as conn:
            result = conn.execute(query).mappings().all()
        return result
