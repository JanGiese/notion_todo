"""Helper class to parse Notion properties."""
from datetime import datetime
import logging

DATE_FORMAT = '%Y-%m-%d'
DATETIME_FORMAT = DATE_FORMAT + 'T%H:%M:%S.%f%z'
class NotionPropertyHelper:
    """Helper class to parse Notion properties."""

    @staticmethod
    def get_property_by_id(id, data):
        """Get property by id."""
        key = NotionPropertyHelper._get_property_key_by_id(id, data)
        return NotionPropertyHelper._property(data['properties'][key])

    @staticmethod
    def set_property_by_id(id, value, data):
        """Set property by id."""
        key = NotionPropertyHelper._get_property_key_by_id(id, data)
        if key:
            data['properties'][key] = NotionPropertyHelper._property(data['properties'][key], value)
        return data

    @staticmethod
    def del_properties_except(ids, properties):
        """Delete properties except param."""
        delete_properties = []
        for name, attr in properties.items():
            if attr['id'] not in ids:
                delete_properties.append(name)
        for name in delete_properties:
            del properties[name]
        return properties

    @staticmethod
    def del_property_by_id(id, data):
        """Delete property by id."""
        key = NotionPropertyHelper._get_property_key_by_id(id, data)
        if key:
            del data['properties'][key]
        return data


    @staticmethod
    def _get_property_key_by_id(id, data):
        for name, attr in data['properties'].items():
            if 'id' in attr and attr['id'] == id:
                return name

    @staticmethod
    def _property(prop, value=None):
        prop_type = prop['type']
        if prop_type in ['checkbox', 'number', 'string']:
            return prop[prop_type]
        if prop_type == 'date':
            return NotionPropertyHelper._date(prop, value)
        elif prop_type == 'multi_select':
            return NotionPropertyHelper._parse_multi_select(prop)
        elif prop_type == 'select':
            return NotionPropertyHelper._parse_select(prop)
        elif prop_type == 'last_edited_by':
            return NotionPropertyHelper._parse_last_edited_by(prop)
        elif prop_type == 'last_edited_time':
            return NotionPropertyHelper._parse_last_edited_time(prop)
        elif prop_type == 'relation':
            return NotionPropertyHelper._parse_relation(prop)
        elif prop_type == 'formula':
            return NotionPropertyHelper._parse_formula(prop)
        elif prop_type == 'title':
            return NotionPropertyHelper._title(prop, value)
        elif prop_type == 'rich_text':
            return NotionPropertyHelper._rich_text(prop, value)
        elif prop_type == 'rollup':
            return NotionPropertyHelper._property(prop['rollup'])
        elif prop_type == 'array':
            return NotionPropertyHelper._parse_array(prop)
        elif prop_type == 'status':
            return NotionPropertyHelper._status(prop, value)
        logging.error(f'No parser for attribute type {prop_type}')
        return None

    @staticmethod
    def _date(prop, value=None):
        if value:
            prop['date'] = {'start': value}
            if 'name' in prop:
                del prop['name']
            return prop
        else:
            if not prop['date']:
                logging.warning(f'No date provided: {prop}')
                return None
            start_date = prop['date']['start']
            if start_date and len(start_date) > 10:
                return datetime.strptime(start_date, DATETIME_FORMAT)
            elif start_date:
                return datetime.strptime(start_date, DATE_FORMAT)
            else:
                logging.warning(f'No date provided: {prop}')
                return None

    @staticmethod
    def _parse_multi_select(prop):
        selected_items = []
        prop_value = prop['multi_select']
        if prop_value:
            for selected_item in prop_value:
                selected_items.append(selected_item['name'])
        return selected_items

    @staticmethod
    def _parse_select(prop):
        prop_value = prop['select']
        if prop_value:
            return prop_value['name']
        return None

    @staticmethod
    def _parse_last_edited_by(prop):
        return prop['last_edited_by']['name']

    @staticmethod
    def _parse_last_edited_time(prop):
        return datetime.strptime(prop['last_edited_time'], DATETIME_FORMAT)

    @staticmethod
    def _parse_relation(prop):
        related_items = []
        prop_value = prop['relation']
        if prop_value:
            for related_item in prop_value:
                related_items.append(related_item['id'])
        return related_items

    @staticmethod
    def _parse_formula(prop):
        return NotionPropertyHelper._property(prop['formula'])

    @staticmethod
    def _title(prop, value=None):
        return NotionPropertyHelper._text(prop, 'title', value)

    @staticmethod
    def _rich_text(prop, value=None):
        return NotionPropertyHelper._text(prop, 'rich_text', value)

    @staticmethod
    def _text(prop, prop_type, value=None):
        if value:
            prop[prop_type] = [{'type': 'text', 'text': {'content': value}}]
            if 'name' in prop:
                del prop['name']
            return prop
        else:
            text = ''
            for line in prop[prop_type]:
                text += line['plain_text'] + '\n'
            return text

    @staticmethod
    def _parse_array(prop):
        item_list = []
        for item in prop['array']:
            parsed_item = NotionPropertyHelper._property(item)
            item_list.append(parsed_item)
        return item_list

    @staticmethod
    def _status(prop, value = None):
        if value:
            return {"type": "status", "status": {"id": value}}
        else:
            return prop['status']['id']
