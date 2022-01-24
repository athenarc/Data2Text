from utils.query_pattern_recognition import QueryInfo


def is_small_select(query_info: QueryInfo):
    if query_info.select['columns_num'] <= 2 and \
            query_info.select['*'] is False and \
            query_info.flags['groupby'] is False and \
            query_info.flags['having'] is False and \
            query_info.flags['joins'] is False and \
            query_info.flags['aggregates'] is False and \
            query_info.flags['distinct'] is False and \
            query_info.flags['orderby'] is False:
        return True
    return False


def is_large_select(query_info: QueryInfo):
    if (query_info.select['columns_num'] > 2 or query_info.select['*'] is True) and\
            query_info.flags['groupby'] is False and \
            query_info.flags['having'] is False and \
            query_info.flags['joins'] is False and \
            query_info.flags['aggregates'] is False and \
            query_info.flags['distinct'] is False and \
            query_info.flags['orderby'] is False:
        return True
    return False


def is_aggregates(query_info: QueryInfo):
    if query_info.flags['select'] is True and \
            query_info.flags['groupby'] is False and \
            query_info.flags['having'] is False and \
            query_info.flags['joins'] is False and \
            query_info.flags['aggregates'] is True and \
            query_info.flags['distinct'] is False:
        return True
    return False


def is_aggregates_and_group_by(query_info: QueryInfo):
    if query_info.flags['select'] is True and \
            query_info.flags['groupby'] is True and \
            query_info.flags['joins'] is False and \
            query_info.flags['aggregates'] is True and \
            query_info.flags['distinct'] is False:
        return True
    return False


def is_join(query_info: QueryInfo):
    if query_info.flags['select'] is True and \
            query_info.flags['groupby'] is False and \
            query_info.flags['having'] is False and \
            query_info.flags['joins'] is True and \
            query_info.flags['aggregates'] is False and \
            query_info.flags['distinct'] is False:
        return True
    return False


def is_join_and_aggregate(query_info: QueryInfo):
    if query_info.flags['select'] is True and \
            query_info.flags['having'] is False and \
            query_info.flags['joins'] is True and \
            query_info.flags['aggregates'] is True and \
            query_info.flags['distinct'] is False:
        return True
    return False
