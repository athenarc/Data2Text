import mo_sql_parsing


class ExtractException(Exception):
    def __init__(self, problem, clause):
        self.message = problem + ": " + str(clause) + "\n"
        super().__init__(self.message)


class OperatorType:
    def __init__(self, members):
        # operators in this category
        self.members = members

        self.num = 0
        self.where = set()
        self.which = set()

    def hasMember(self, op):
        return op in self.members

    def update(self, where, which):
        self.num += 1
        self.where.add(where)
        self.which.add(which)

    def __str__(self):
        return "num: " + str(self.num) + ", where: " + str(self.where) + ", which: " + str(self.which)


# Info for a query parsed with the mo_sql parser
class QueryInfo:

    clauses = {'select_distinct', 'select', 'from', 'where', 'groupby', 'having', 'orderby', 'limit', 'intersect', 'union', 'except'}

    def __init__(self, query):
        parsed_query = mo_sql_parsing.parse(query)
        # clauses
        self.select = {"columns_num": 0, "*": False}
        self.from_clause = {"tables_num": 0}
        self.where = False
        self.groupby = {"columns_num": 0}
        self.having = False
        self.orderby = {"columns_num": 0}
        self.limit = False

        # operators
        self.aggregates = OperatorType({'count', 'min', 'max', 'sum', 'avg'})
        self.numerical_operators = OperatorType({'gt', 'gte', 'lt', 'lte', 'eq', 'neq', 'between'})
        self.logical_operators = OperatorType({'and', 'or'})
        self.like_operators = OperatorType({'like', 'not_like'})
        self.arithmetic_operators = OperatorType({'sub', 'add'})
        self.membership_operators = OperatorType({'in', 'nin'})

        self.numerical_constraints = {"num": 0, "where": set()}
        self.literals = {"num": 0, "where": set()}
        self.distinct = {"num": 0, "where": set()}

        self.joins = {"num": 0}

        # TODO add info for where??
        # subqueries
        self.intersect = []
        self.union = []
        self.except_clause = []
        self.nesting = []

        self._extract_info(parsed_query)

    # Returns a dictionary with keys: all tested conditions and values: boolean, existence of each condition
    @property
    def flags(self):
        return {
            "select": self.select["*"] is True or self.select["columns_num"] != 0,
            "from_clause": self.from_clause["tables_num"] != 0,
            "where": self.where,
            "groupby": self.groupby["columns_num"] != 0,
            "having": self.having,
            "orderby": self.orderby["columns_num"] != 0,
            "limit": self.limit,
            "intersect": len(self.intersect) != 0,
            "except_clause": len(self.except_clause) != 0,
            "union": len(self.union) != 0,
            "nesting": len(self.nesting) != 0,
            "joins": self.joins["num"] != 0,
            "aggregates": self.aggregates.num != 0,
            "logical_operators": self.logical_operators.num != 0,
            "numerical_operators": self.numerical_operators.num != 0,
            "like_operators": self.like_operators.num != 0,
            "arithmetic_operators": self.arithmetic_operators.num != 0,
            "membership_operators": self.membership_operators.num != 0,
            "numerical_constraints": self.numerical_constraints['num'] != 0,
            "literals": self.literals["num"] != 0,
            "distinct": self.distinct["num"] != 0
        }

    @property
    def category(self):
        category = ""
        description = []
        for flag, value in self.flags.items():
            category += ('1' if value else '0')
            if value:
                description.append(flag)
        return {"name": category, "description": "-".join(description)}

    def _extract_info(self, query):
        for clause in self.clauses:
            # if the clause exists in the query
            if clause in list(query.keys()):
                getattr(self, "_extract_%s_info" % clause)(query[clause])

    def _extract_select_distinct_info(self, select):
        self.distinct["num"] += 1
        self.distinct["where"].add('select')
        self._extract_select_info(select)

    def _extract_select_info(self, select_clause):
        try:
            select_type = type(select_clause)
            if select_type is list:
                self.select['columns_num'] = len(select_clause)
                for column in select_clause:
                    self._extract_parameters_info(column["value"], "select")
            elif select_type is str:
                self.select['*'] = True
                self.select['column_num'] = None
            else:
                self.select['columns_num'] = 1
                self._extract_parameters_info(select_clause["value"], "select")
        except:
            raise ExtractException('Not considered case for select clause', select_clause)

    def _extract_from_info(self, from_clause):
        try:
            from_type = type(from_clause)
            # If from has only one table
            if from_type is str:
                self.from_clause['tables_num'] = 1
            # If from clause has joins
            elif from_type is list:
                self.from_clause['tables_num'] = len(from_clause)
                self._extract_joins_info(from_clause[1:], "from")
            else:  # If from_clause is a dict
                keys = from_clause.keys()
                # If the from clause has a subquery
                if "select" in keys:
                    self.from_clause['tables_num'] = 1
                    self._extract_nesting_info(from_clause)
                # If from has one table with an alias
                elif "value" in keys:
                    self.from_clause['tables_num'] = 1
                # TODO check if the length of the dict is 1?
                else:
                    self.from_clause['tables_num'] = 1
                    key = list(from_clause.keys())[0]
                    self._extract_parameters_info(from_clause[key], "from")
        except:
            raise ExtractException('Not considered case for from clause', from_clause)

    def _extract_where_info(self, where_clause):
        try:
            self.where = True
            self._extract_parameters_info(where_clause, "where")
        except:
            raise ExtractException('Not considered case for where clause', where_clause)

    def _extract_groupby_info(self, groupby_clause):
        try:
            groupby_type = type(groupby_clause)
            # If groupby has multiple columns
            if groupby_type is list:
                self.groupby['columns_num'] = len(groupby_clause)
                for col in groupby_clause:
                    self._extract_parameters_info(col["value"], "groupby")
            else:  # If groupby has only one column
                self.groupby['columns_num'] = 1
                self._extract_parameters_info(groupby_clause["value"], "groupby")
        except:
            raise ExtractException('Not considered case for groupby clause', groupby_clause)

    def _extract_having_info(self, having_clause):
        try:
            self.having = True
            self._extract_parameters_info(having_clause, "having")
        except:
            raise ExtractException('Not considered case for having clause', having_clause)

    def _extract_orderby_info(self, orderby_clause):
        try:
            orderby_type = type(orderby_clause)
            # If orderby has multiple columns
            if orderby_type is list:
                self.orderby['columns_num'] = len(orderby_clause)
                for col in orderby_clause:
                    self._extract_parameters_info(col["value"], "orderby")
            else:  # If orderby has only one column
                self.orderby['columns_num'] = 1
                self._extract_parameters_info(orderby_clause["value"], "orderby")
        except:
            raise ExtractException('Not considered case for orderby clause', orderby_clause)

    def _extract_limit_info(self, limit_clause):
        self.limit = True

    def _extract_intersect_info(self, intersect_clause):
        try:
            self.intersect.append((QueryInfo(intersect_clause[0]), QueryInfo(intersect_clause[1])))
        except:
            raise ExtractException('Not considered case for intersect clause', intersect_clause)

    def _extract_except_info(self, except_clause):
        try:
            self.except_clause.append((QueryInfo(except_clause[0]), QueryInfo(except_clause[1])))
        except:
            raise ExtractException('Not considered case for except clause', except_clause)

    def _extract_union_info(self, union_clause):
        try:
            self.union.append((QueryInfo(union_clause[0]), QueryInfo(union_clause[1])))
        except:
            raise ExtractException('Not considered case for union clause', union_clause)

    def _extract_nesting_info(self, nested_clause):
        try:
            self.nesting.append(QueryInfo(nested_clause))
        except:
            raise ExtractException('Not considered case for nested clause', nested_clause)

    def _extract_parameters_info(self, parameters, clause):
        try:
            parameters_type = type(parameters)
            # If parameters is a variable
            if parameters_type is str:
                pass
            # If parameters is a number
            elif parameters_type in [int, float]:
                self.numerical_constraints["num"] += 1
                self.numerical_constraints["where"].add(clause)
            elif parameters_type is list:
                for p in parameters:
                    self._extract_parameters_info(p, clause)
            else:  # If parameters is a dict
                keys = list(parameters.keys())
                # If parameters is a subquery
                if "select" in keys or "select_distinct" in keys:
                    self.nesting.append(QueryInfo(parameters))
                else:
                    # TODO check for the length of keys (1)?
                    key = keys[0]
                    if key == "literal":
                        self.literals["num"] += 1
                        self.literals["where"].add(clause)
                    elif key == "distinct":
                        self.distinct["num"] += 1
                        self.distinct["where"].add(clause)
                    elif "intersect" == key:
                        self._extract_intersect_info(parameters["intersect"])
                    elif "except" == key:
                        self._extract_except_info(parameters["except"])
                    elif "union" == key:
                        self._extract_union_info(parameters["union"])
                    # TODO find better way
                    elif self.aggregates.hasMember(key):
                        self.aggregates.update(clause, key)
                        self._extract_parameters_info(parameters[key], clause)
                    elif self.numerical_operators.hasMember(key):
                        self.numerical_operators.update(clause, key)
                        self._extract_parameters_info(parameters[key], clause)
                    elif self.logical_operators.hasMember(key):
                        self.logical_operators.update(clause, key)
                        self._extract_parameters_info(parameters[key], clause)
                    elif self.arithmetic_operators.hasMember(key):
                        self.arithmetic_operators.update(clause, key)
                        self._extract_parameters_info(parameters[key], clause)
                    elif self.membership_operators.hasMember(key):
                        self.membership_operators.update(clause, key)
                        self._extract_parameters_info(parameters[key], clause)
                    else:  # key in like_operators
                        self.like_operators.update(clause, key)
                        self._extract_parameters_info(parameters[key], clause)
        except:
            raise ExtractException('Not considered case for parameters', parameters)

    def _extract_joins_info(self, joins, clause):
        try:
            for join in joins:
                self.joins["num"] += 1
                if "on" in join.keys():
                    self._extract_parameters_info(join["on"], clause)
        except:
            raise ExtractException('Not considered case for joins', joins)
