#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
import json
import sys

from elasticsearch import Elasticsearch


def determine_materialization_value_doc_count(materialization_value_query,
                                              elasticsearch_instance,
                                              elasticsearch_index_name,
                                              elasticsearch_index_type):
    materialization_value_doc_count_response = elasticsearch_instance.count(
        index=elasticsearch_index_name,
        doc_type=elasticsearch_index_type,
        body=materialization_value_query
    )
    return materialization_value_doc_count_response['count']


def retrieve_materialization_values(seed_field,
                                    seed_value,
                                    materialization_field,
                                    elasticsearch_instance,
                                    elasticsearch_index_name,
                                    elasticsearch_index_type):
    materialization_field_keyword = materialization_field + '.keyword'
    seed_field_keyword = seed_field + '.keyword'
    materialization_value_query = {"query": {"bool": {
        "must": [{"exists": {"field": materialization_field_keyword}}, {"match": {seed_field_keyword: seed_value}}]}}}
    materialization_value_doc_count = determine_materialization_value_doc_count(materialization_value_query,
                                                                                elasticsearch_instance,
                                                                                elasticsearch_index_name,
                                                                                elasticsearch_index_type)

    if materialization_value_doc_count == 0:
        return None

    materialization_value_response = elasticsearch_instance.search(
        index=elasticsearch_index_name,
        doc_type=elasticsearch_index_type,
        body=materialization_value_query,
        _source=[materialization_field],
        filter_path=['hits.hits._source.' + materialization_field],
        size=materialization_value_doc_count
    )

    materialization_value_records = materialization_value_response['hits']['hits']
    if materialization_value_doc_count == 1:
        return materialization_value_records[0]['_source'][materialization_field]

    materialization_values = []
    for record in materialization_value_records:
        materialization_values.append(record['_source'][materialization_field])

    return materialization_values


def retrieve_materialization_value_count(seed_field,
                                         seed_value,
                                         materialization_field,
                                         elasticsearch_instance,
                                         elasticsearch_index_name,
                                         elasticsearch_index_type):
    materialization_field_keyword = materialization_field + '.keyword'
    seed_field_keyword = seed_field + '.keyword'
    materialization_value_count_query = {"aggs": {"materialization_value_count": {"filter": {"bool": {
        "must": [{"exists": {"field": materialization_field_keyword}}, {"match": {seed_field_keyword: seed_value}}]}},
        "aggs": {"value_count": {
            "value_count": {
                "field": materialization_field_keyword}}}}}}
    materialization_value_count_response = elasticsearch_instance.search(
        index=elasticsearch_index_name,
        doc_type=elasticsearch_index_type,
        body=materialization_value_count_query,
        size=0
    )
    materialization_value_count = \
        materialization_value_count_response['aggregations']['materialization_value_count']['value_count'][
            'value']

    if materialization_value_count == 0:
        return None

    return materialization_value_count


def add_materialization_values(elasticsearch_index_name,
                               elasticsearch_index_type,
                               elasticsearch_instance,
                               json_record,
                               materialization_field,
                               seed_field,
                               seed_values,
                               target_field,
                               target_field_is_singlevalued):
    all_materialization_values = []
    for seed_value in seed_values:
        materialization_values = retrieve_materialization_values(seed_field,
                                                                 seed_value,
                                                                 materialization_field,
                                                                 elasticsearch_instance,
                                                                 elasticsearch_index_name,
                                                                 elasticsearch_index_type)
        if materialization_values is not None:
            all_materialization_values.append(materialization_values)

    if len(all_materialization_values) > 0:
        if len(all_materialization_values) == 1:
            result_materialization_values = all_materialization_values[0]
        else:
            result_materialization_values = []
            for materialization_value in all_materialization_values:
                if isinstance(materialization_value, list):
                    for single_materialization_value in materialization_value:
                        result_materialization_values.append(single_materialization_value)
                else:
                    result_materialization_values.append(materialization_value)
        # materialize result
        if not target_field_is_singlevalued and not isinstance(result_materialization_values, list):
            json_record[target_field] = [result_materialization_values]
        elif target_field_is_singlevalued and isinstance(result_materialization_values, list) and len(
                result_materialization_values) == 1:
            json_record[target_field] = result_materialization_values[0]
        else:
            json_record[target_field] = result_materialization_values

    return json_record


def add_materialization_value_count(elasticsearch_index_name,
                                    elasticsearch_index_type,
                                    elasticsearch_instance,
                                    json_record,
                                    materialization_field,
                                    seed_field,
                                    seed_values,
                                    target_field):
    all_materialization_value_count = 0
    for seed_value in seed_values:
        materialization_value_count = retrieve_materialization_value_count(seed_field,
                                                                           seed_value,
                                                                           materialization_field,
                                                                           elasticsearch_instance,
                                                                           elasticsearch_index_name,
                                                                           elasticsearch_index_type)
        if materialization_value_count is not None:
            all_materialization_value_count += materialization_value_count

    if all_materialization_value_count > 0:
        json_record[target_field] = all_materialization_value_count

    return json_record


def run():
    parser = argparse.ArgumentParser(prog='ldjesmaterializer',
                                     description='takes line-delimited JSON records and some arguments as input and materializes information from other records (stored in an elasticsearch index) into them',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    optional_arguments = parser._action_groups.pop()

    required_arguments = parser.add_argument_group('required arguments')
    required_arguments.add_argument('-elasticsearch-index-name', type=str, dest='elasticsearch_index_name',
                                    help='the name of the elasticsearch index to use', required=True)
    required_arguments.add_argument('-elasticsearch-index-type', type=str, dest='elasticsearch_index_type',
                                    help='elasticsearch index (document) type to use', required=True)
    required_arguments.add_argument('-source-field', type=str, dest='source_field',
                                    help='the field name in the (source) record whose value should be used to request the records for materialization',
                                    required=True)
    required_arguments.add_argument('-seed-field', type=str, dest='seed_field',
                                    help='the field name in the records in the elasticsearch index that should be used to request the records with the seed value for materialization',
                                    required=True)
    required_arguments.add_argument('-materialization-field', type=str, dest='materialization_field',
                                    help='the field name in the records in the elasticsearch index that contains the information for materialization',
                                    required=True)
    required_arguments.add_argument('-target-field', type=str, dest='target_field',
                                    help='the field name in the (target) records that should be used to write the information retrieved from the materialization request to the elasticsearch index',
                                    required=True)

    optional_arguments.add_argument('-elasticsearch-instance-host', dest='elasticsearch_instance_host', type=str,
                                    default='localhost',
                                    help='hostname or IP address of the elasticsearch instance to use')
    optional_arguments.add_argument('-elasticsearch-instance-port', dest='elasticsearch_instance_port', type=int,
                                    default=9200,
                                    help='port of the elasticsearch instance to use')
    optional_arguments.add_argument('-target-field-is-singlevalued', action="store_true",
                                    dest='target_field_is_singlevalued',
                                    help='indicates, whether the target field should be a JSON array (for multiple values) or a JSON object / simple value (for single values); default is false, i.e., the retrieved values will be written into a JSON array')
    optional_arguments.add_argument('-materialization-value-count-only', action="store_true",
                                    dest='materialization_value_count_only',
                                    help='indicates, whether the only the materialization value count should be written into the target field')

    parser._action_groups.append(optional_arguments)

    args = parser.parse_args()

    elasticsearch_instance_host = args.elasticsearch_instance_host
    elasticsearch_instance_port = args.elasticsearch_instance_port
    source_field = args.source_field
    seed_field = args.seed_field
    materialization_field = args.materialization_field
    target_field = args.target_field
    elasticsearch_index_name = args.elasticsearch_index_name
    elasticsearch_index_type = args.elasticsearch_index_type
    target_field_is_singlevalued = args.target_field_is_singlevalued
    materialization_value_count_only = args.materialization_value_count_only

    elasticsearch_instance = Elasticsearch([{'host': elasticsearch_instance_host}], port=elasticsearch_instance_port)

    for line in sys.stdin:
        json_record = json.loads(line)
        seed_value = json_record[source_field]

        if seed_value is not None:
            if isinstance(seed_value, list):
                seed_values = seed_value
            else:
                seed_values = [seed_value]

            if not materialization_value_count_only:
                enhanced_json_record = add_materialization_values(elasticsearch_index_name,
                                                                  elasticsearch_index_type,
                                                                  elasticsearch_instance,
                                                                  json_record,
                                                                  materialization_field,
                                                                  seed_field,
                                                                  seed_values,
                                                                  target_field,
                                                                  target_field_is_singlevalued)
            else:
                enhanced_json_record = add_materialization_value_count(elasticsearch_index_name,
                                                                       elasticsearch_index_type,
                                                                       elasticsearch_instance,
                                                                       json_record,
                                                                       materialization_field,
                                                                       seed_field,
                                                                       seed_values,
                                                                       target_field)
        else:
            enhanced_json_record = json_record

        sys.stdout.write(json.dumps(enhanced_json_record, indent=None) + "\n")


if __name__ == "__main__":
    run()
