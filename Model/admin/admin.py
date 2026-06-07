from config import engine
from sqlalchemy import text
class Admin:
    @staticmethod
    def build_filters(code=None, name=None, category=None, tradeshow=None, year=None):
        params = {}
        filters = []

        need_join = any([code, name, category, tradeshow])
        join_clause = ""

        if need_join:
            join_clause = """
                    JOIN drm_nts_messages m 
                    ON m.code = v.agent_code
                """

            if code:
                filters.append("m.code ILIKE :code")
                params["code"] = f"%{code}%"

            if name:
                filters.append("m.name ILIKE :name")
                params["name"] = f"%{name}%"

            if category:
                categories = [c.strip() for c in category.split(",")]
                filters.append("m.category = ANY(:category)")
                params["category"] = categories

            if tradeshow:
                filters.append("m.message_text ILIKE :tradeshow")
                params["tradeshow"] = f"%{tradeshow}%"

        # year filter
        if year:
            filters.append("""
                    EXTRACT(YEAR FROM v.last_service_date) = :year
                """)
            params["year"] = int(year)

        else:
            filters.append("""
                    EXTRACT(YEAR FROM v.last_service_date) >= 2025
                """)

        where_clause = ""

        if filters:
            where_clause = "WHERE " + " AND ".join(filters)

        return join_clause, where_clause, params

    @staticmethod
    def get_revenue_quarter(code=None, name = None, category=None, tradeshow=None, year=None):
        join_clause, where_clause, params = Admin.build_filters(
            code, name, category, tradeshow, year
        )

        sql = text(f"""
            SELECT
                EXTRACT(YEAR FROM v.last_service_date)::int AS year,

                CASE
                    WHEN EXTRACT(MONTH FROM v.last_service_date) BETWEEN 1 AND 3 THEN 'Q1'
                    WHEN EXTRACT(MONTH FROM v.last_service_date) BETWEEN 4 AND 6 THEN 'Q2'
                    WHEN EXTRACT(MONTH FROM v.last_service_date) BETWEEN 7 AND 9 THEN 'Q3'
                    ELSE 'Q4'
                END AS quarter,

                SUM(v.profit) AS revenue

            FROM "View_Revenue_By_Agent" v

            {join_clause}

            {where_clause}

            GROUP BY
                EXTRACT(YEAR FROM v.last_service_date),
                quarter

            ORDER BY year, quarter
        """)

        with engine.connect() as conn:
            rows = [
                dict(r)
                for r in conn.execute(sql, params).mappings().all()
            ]
        return rows

    @staticmethod
    def get_revenue_monthly(code=None,name=None,category=None,tradeshow=None,year=None):
        join_clause, where_clause, params = Admin.build_filters(
            code, name, category, tradeshow, year
        )

        sql = text(f"""
                    SELECT
                        EXTRACT(MONTH FROM v.last_service_date)::int AS month,

                        SUM(v.profit) AS revenue

                    FROM "View_Revenue_By_Agent" v

                    {join_clause}

                    {where_clause}

                    GROUP BY month

                    ORDER BY month
                """)

        with engine.connect() as conn:
            rows = [
                dict(r)
                for r in conn.execute(sql, params).mappings().all()
            ]
        return rows

    @staticmethod
    def get_top_agents(code=None, name=None, category=None, tradeshow=None, year=None):
        join_clause, where_clause, params = Admin.build_filters(
            code, name, category, tradeshow, year
        )
        if not join_clause:
            join_clause = """
                LEFT JOIN drm_nts_messages m
                    ON m.code = v.agent_code
            """
        sql = text(f"""
                        SELECT
                            v.agent_code,

                            MAX(m.name) AS name,
                
                            SUM(v.profit) AS revenue

                        FROM "View_Revenue_By_Agent" v

                        {join_clause}

                        {where_clause}

                        GROUP BY v.agent_code

                        ORDER BY revenue DESC
                        
                        LIMIT 10
                    """)

        with engine.connect() as conn:
            rows = [
                dict(r)
                for r in conn.execute(sql, params).mappings().all()
            ]
        return rows

    @staticmethod
    def get_revenue_quarter_detail(quarter,year=None,code = None,name = None,category = None,tradeshow = None,from_date=None,to_date=None):

        quarter_condition = {
            'Q1': 'BETWEEN 1 AND 3',
            'Q2': 'BETWEEN 4 AND 6',
            'Q3': 'BETWEEN 7 AND 9',
            'Q4': 'BETWEEN 10 AND 12'
        }

        month_sql = quarter_condition.get(quarter)

        filters = []
        params = {}

        need_join = any([
            code,
            name,
            category,
            tradeshow
        ])
        join_clause = ""
        if need_join:
            join_clause = """
                    JOIN drm_nts_messages m
                        ON m.code = agent_code
                """

        if code:
            filters.append("m.code ILIKE :code")
            params["code"] = f"%{code}%"

        if name:
            filters.append("m.name ILIKE :name")
            params["name"] = f"%{name}%"

        if category:
            categories = [c.strip() for c in category.split(",")]
            filters.append("m.category = ANY(:category)")
            params["category"] = categories

        if tradeshow:
            filters.append("m.message_text ILIKE :tradeshow")
            params["tradeshow"] = f"%{tradeshow}%"


        # ===== YEAR =====

        if year:

            filters.append("""
                EXTRACT(YEAR FROM last_service_date) = :year
            """)

            params['year'] = int(year)

        else:

            filters.append("""
                EXTRACT(YEAR FROM last_service_date) >= 2025
            """)

        # ===== QUARTER =====

        if month_sql:
            filters.append(f"""
                EXTRACT(MONTH FROM last_service_date)
                    {month_sql}
            """)

        # ===== FROM DATE =====

        if from_date:
            filters.append("""
                last_service_date::date >= :from_date
            """)

            params['from_date'] = from_date

        # ===== TO DATE =====

        if to_date:
            filters.append("""
                last_service_date::date <= :to_date
            """)

            params['to_date'] = to_date

        # ===== WHERE =====

        where_clause = ""

        if filters:
            where_clause = """
                WHERE
            """ + " AND ".join(filters)

        # ===== SQL =====

        sql = text(f"""

            SELECT

                EXTRACT(YEAR FROM last_service_date)::int
                    AS year,

                EXTRACT(MONTH FROM last_service_date)::int
                    AS month,

                last_service_date::date
                    AS service_date,

                agent_code,

                agent_name,

                SUM(profit) AS revenue

            FROM "View_Revenue_By_Agent"
            {join_clause}
            {where_clause}

            GROUP BY

                EXTRACT(YEAR FROM last_service_date),

                EXTRACT(MONTH FROM last_service_date),

                last_service_date::date,

                agent_code,

                agent_name

            ORDER BY

                EXTRACT(YEAR FROM last_service_date) ASC,

                EXTRACT(MONTH FROM last_service_date) ASC,

                last_service_date::date ASC,

                revenue DESC
        """)

        with engine.connect() as conn:

            rows = conn.execute(
                sql,
                params
            ).mappings().all()

        return [
            dict(r)
            for r in rows
        ]

    @staticmethod
    def get_revenue_monthly_detail(month,year=None,code=None,name=None,category=None,tradeshow=None,from_date=None, to_date=None):

        join_clause, where_clause, params = Admin.build_filters(
            code,
            name,
            category,
            tradeshow,
            year
        )

        filters = []

        # ===== MONTH =====

        if month:
            filters.append("""
                EXTRACT(MONTH FROM v.last_service_date) = :month
            """)

            params['month'] = int(month)

        # ===== FROM DATE =====

        if from_date:
            filters.append("""
                v.last_service_date::date >= :from_date
            """)

            params['from_date'] = from_date

        # ===== TO DATE =====

        if to_date:
            filters.append("""
                v.last_service_date::date <= :to_date
            """)

            params['to_date'] = to_date

        extra_where = ""

        if filters:

            if where_clause:

                extra_where = " AND " + " AND ".join(filters)

            else:

                extra_where = " WHERE " + " AND ".join(filters)

        sql = text(f"""

            SELECT

                EXTRACT(YEAR FROM v.last_service_date)::int
                    AS year,

                EXTRACT(MONTH FROM v.last_service_date)::int
                    AS month,

                v.last_service_date::date
                    AS service_date,

                v.agent_code,

                v.agent_name,

                SUM(v.profit) AS revenue

            FROM "View_Revenue_By_Agent" v

            {join_clause}

            {where_clause}

            {extra_where}

            GROUP BY

                EXTRACT(YEAR FROM v.last_service_date),

                EXTRACT(MONTH FROM v.last_service_date),

                v.last_service_date::date,

                v.agent_code,

                v.agent_name

            ORDER BY

                year ASC,

                month ASC,

                service_date ASC,

                revenue DESC
        """)

        with engine.connect() as conn:

            rows = conn.execute(
                sql,
                params
            ).mappings().all()

        return [dict(r) for r in rows]

    @staticmethod
    def get_top_agents_detail(agent_code,year=None,code=None,name=None,category=None,tradeshow=None,from_date=None,to_date=None):

        join_clause, where_clause, params = Admin.build_filters(
            code,
            name,
            category,
            tradeshow,
            year
        )

        if not join_clause:
            join_clause = """
                LEFT JOIN drm_nts_messages m
                    ON m.code = v.agent_code
            """

        filters = []

        # ===== AGENT =====

        if agent_code:
            filters.append("""
                v.agent_code = :agent_code
            """)

            params['agent_code'] = agent_code

        # ===== FROM DATE =====

        if from_date:
            filters.append("""
                v.last_service_date::date >= :from_date
            """)

            params['from_date'] = from_date

        # ===== TO DATE =====

        if to_date:
            filters.append("""
                v.last_service_date::date <= :to_date
            """)

            params['to_date'] = to_date

        extra_where = ""

        if filters:

            if where_clause:

                extra_where = " AND " + " AND ".join(filters)

            else:

                extra_where = " WHERE " + " AND ".join(filters)

        sql = text(f"""

            SELECT

                EXTRACT(YEAR FROM v.last_service_date)::int
                    AS year,

                EXTRACT(MONTH FROM v.last_service_date)::int
                    AS month,

                v.last_service_date::date
                    AS service_date,

                v.agent_code,

                MAX(m.name) AS agent_name,

                SUM(v.profit) AS revenue

            FROM "View_Revenue_By_Agent" v

            {join_clause}

            {where_clause}

            {extra_where}

            GROUP BY

                EXTRACT(YEAR FROM v.last_service_date),

                EXTRACT(MONTH FROM v.last_service_date),

                v.last_service_date::date,

                v.agent_code

            ORDER BY

                year ASC,

                month ASC,

                service_date ASC,

                revenue DESC
        """)

        with engine.connect() as conn:

            rows = conn.execute(
                sql,
                params
            ).mappings().all()

        return [dict(r) for r in rows]