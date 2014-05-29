import base64
import uuid
import os
import shutil

from bs4 import BeautifulSoup
import nltk

from util import Util


class Condition:
    def __init__(self):
        self.conditions = {}

    def get_names(self):
        return self.conditions.keys()

    def get_name(self, value):
        try:
            dict = self.conditions
            key = dict.keys()[dict.values().index(value)]
            return key
        except:
            return 'UNKNOWN'

    def get_value(self, key):
        try:
            return self.conditions[key]
        except:
            return -100


class Operation:
    def __init__(self):
        self.operations = {'Equal': 0,
                           'Not Equal': 1,
                           'Greater Than': 2,
                           'Greater Than or Equal': 20,
                           'Less Than': 3,
                           'Less Than or Equal': 21,
                           'Contain': 4,
                           'Not Contain': 5,
                           'Is Blank': 12,
                           'Is Not Blank': 13,
                           'Contained Within': 14,
                           'Not Contained Within': 15,
                           'Starts With': 16,
                           'Not Starts With': 17,
                           'Ends With': 18,
                           'Not Ends With': 19,
                           'Contains Any': 34,
                           'Not Contains Any': 35}


    def get_names(self):
        return self.operations.keys()

    def get_name(self, value):
        try:
            dict = self.operations
            key = dict.keys()[dict.values().index(value)]
            return key
        except:
            return 'UNKNOWN'

    def get_value(self, key):
        try:
            return self.operations[key]
        except:
            return -100


class SubPageCondition(Condition):
    def __init__(self):
        self.conditions = {'Client Conditions': 0,
                           'Partner Conditions': 1,
                           'Client Scenario Conditions': 3,
                           'Partner Scenario Conditions': 4,
                           'User Conditions': 2}


class OtherCondition(Condition):
    def __init__(self):
        self.conditions = {'Entity Conditions': 0,
                           'Partner Conditions': 1,
                           'Entity Scenario Conditions': 3,
                           'Partner Scenario Conditions': 4}


class XPlanItem:
    def __init__(self):
        self.item = {'d_object_name': '',
                     'd_condition_type': -100, # Client, Partner, User, etc.
                     'd_action_field': '',
                     'd_operation': -100,
                     'd_value': '',
                     'd_reference': '',
                     'x_object_type': '',
                     'x_condition_category': '', # Condition or FieldConditionStore
                     'x_value_in_base64': '',
                     'x_field': '',
                     'x_group': '',
                     'x_operator': '',
                     'x_version': ''}

    def set_d_object_name(self, value):
        self.item['d_object_name'] = value

    def set_d_condition_type(self, value):
        self.item['d_condition_type'] = value

    def set_d_action_field(self, value):
        self.item['d_action_field'] = value

    def set_d_operation(self, value):
        self.item['d_operation'] = value

    def set_d_value(self, value):
        self.item['d_value'] = value

    def set_d_reference(self, value):
        self.item['d_reference'] = value

    def set_x_object_type(self, value):
        self.item['x_object_type'] = value

    def set_x_condition_category(self, value):
        self.item['x_condition_category'] = value

    def set_x_value_in_base64(self, value):
        self.item['x_value_in_base64'] = value

    def set_x_field(self, value):
        self.item['x_field'] = value

    def set_x_group(self, value):
        self.item['x_group'] = value

    def set_x_operator(self, value):
        self.item['x_operator'] = value

    def set_x_version(self, value):
        self.item['x_version'] = value

    def set_all(self, new_dict):
        self.item.update(new_dict)

    def get_item(self):
        return self.item


class XPlanObject:
    def __init__(self):
        self.obj = []

    def append_item(self, new_item):
        self.obj.append(new_item)

    def get_item_by_reference(self, str_reference):
        #for item in self.obj:
        #    i = item.get_item()
        #    if i['reference'] == str_reference:
        #        return i
        return [i for i in self.obj if i.get_item()['d_reference'] == str_reference]

    def get_obj(self):
        obj = self.obj
        #obj.reverse()
        return obj


class XPlan:
    def __init__(self):
        self.filename = 'page.xml'
        self.zipfile = 'page.zip'
        self.tmp_dir = '___tmp___'
        self.soup = BeautifulSoup()

    def load_zip(self):
        if not os.path.exists(self.zipfile):
            print '[error] Cannot find page.zip.'
            return False

        #prepare directory
        try:
            if os.path.isdir(self.tmp_dir):
                print 'Removing ' + self.tmp_dir + ' folder...'
                shutil.rmtree(self.tmp_dir)
        except Exception as e:
            print '[error] Cannot delete __tmp__ folder.'
            return False

        try:
            os.makedirs(self.tmp_dir)
        except Exception as e:
            print '[error] Cannot create __tmp__ folder.'
            return False

        try:
            print 'Extracting ' + self.zipfile + ' file...'
            Util.unzip(self.zipfile, self.tmp_dir)
        except Exception as e:
            print '[error] Cannot extract page.zip .'
            return False

        print 'Loading xml...'
        path = os.path.join(self.tmp_dir, self.filename)
        self.soup = BeautifulSoup(open(path).read())

        #cleanup
        try:
            if os.path.isdir(self.tmp_dir):
                shutil.rmtree(self.tmp_dir)
        except Exception as e:
            print '[error] Cannot delete __tmp__ folder.'
            return False

        return True

    def __append_new_data(self, soap_node, data):
        condition_type = data['d_condition_type']
        if condition_type == -100:
            return

        condition_category = data['x_condition_category']

        pos = 0
        for type_list in soap_node.find_all('object', attrs={"type": "List"}):
            if pos == condition_type:
                if condition_category == 'Condition':
                    type_list.append(self.get_Condition(data))
                elif condition_category == 'FieldConditionStore':
                    type_list.append(self.get_FieldConditionStore(data))
            pos = pos + 1

    def generate_zip_file(self, xplan_object):
        self.xplan_object = xplan_object
        print 'Loading object file...'
        name = os.path.splitext(os.path.basename(self.filename))[0]
        object_file = name + '_obj.xml'
        self.soup = BeautifulSoup(open(object_file).read())

        print 'Updating object file...'
        for object in self.soup.find_all("conditions", attrs={"type": "List"}):
            reference = object.get('reference')
            if not reference:
                continue

            self.__clear_conditions(object)

            for xplan_item in xplan_object.get_item_by_reference(reference):
                data = xplan_item.get_item()
                self.__append_new_data(object, data)

        print 'Saving to zip file...'
        output_zip = name + '_new.zip'
        xml_file = name + '.xml'

        f = open(xml_file, 'w')
        f.write(self.get_xml())
        f.close()

        try:
            shutil.copyfile('page.zip', output_zip)
            Util.append_to_zip(output_zip, xml_file)
        except Exception as e:
            print '[zip:error] ' + str(e)


    def extract_objects(self):
        self.xplan_object = XPlanObject()

        # Sample for FieldConditionStore
        # ------------------------------
        #<conditions type="List">
        #    <object type="List">
        #        <object type="FieldConditionStore">
        #            <object field="consequences_start_managed__fund" operator_value="4" 
        #            value_xml="PEw+PHU+MjA8L3U+PC9MPg==" version="2">
        #            </object>
        #        </object>
        #    </object>
        #</conditions>


        # Sample for Condition
        # --------------------
        #<conditions type="List">
        #    <object type="List">
        #        <object type="Condition">
        #            <object criteria_xml="PEkgbW9kPSJ4cHQuZW50aXR5LnNlYXJjaCIgY2xzPSJTZWFyY2hCeUZpZWxkIj48cz5kZTwvcz48
        #            aT4xPC9pPjxzPmZ0PC9zPjx1PnN0cmVhbTwvdT48cz5mdjwvcz48dT4xPC91PjxzPm9wPC9zPjxp
        #            PjA8L2k+PC9JPg==
        #            " field="" group="" operator="0" store_mode="xmlised" value="" version="4">
        #            </object>
        #        </object>
        #    </object>
        #</conditions>

        print 'Extracting objects...'
        for object in self.soup.find_all("conditions", attrs={"type": "List"}):  # find all <conditions type="List">
            original_object = object
            found_any_condition = False

            # Grab title (object name) and object type
            #
            path_title = []
            path_name = []
            object_type = {'value': '', 'found_first_iteration': False}

            title = object.parent.get('title')
            config_xml = object.parent.get('config_xml')

            if title == None and config_xml == None:
                continue

            while object.parent:  # for each condition found, iterate element upward
                title = object.parent.get('title')
                config_xml = object.parent.get('config_xml')  # hack! Newspeedgroup doesn't have title!

                if title != None or config_xml != None:  # we only interested for element that contains title and config_xml
                    name = object.parent.get('name')
                    obj_type = object.parent.parent.get('type')
                    if object_type['found_first_iteration'] == False:
                        object_type['value'] = obj_type
                        object_type['found_first_iteration'] = True

                    if config_xml:  # Newspeedgroup doesn't have title!
                        title = ''
                    else:
                        title = nltk.clean_html(title)
                    if title:
                        path_title.append(title)
                    else:
                        path_title.append('[' + obj_type + ']')

                    if name:
                        path_name.append(name)

                object = object.parent

            path_title.reverse()
            path_title = "---->".join(path_title)

            path_name.reverse()
            path_name = "---->".join(path_name)

            object_name = path_title + ' {' + path_name + '}'

            #
            #  end grab title

            object = original_object  # reset

            pos = 0
            reference = uuid.uuid1().bytes.encode('base64').rstrip('=\n').replace('/', '_')
            object['reference'] = reference
            for cat in object.find_all("object", attrs={"type": "List"}):  # find all <object type="List">
                for _condition in cat.select('object[type]'):  # grab only <object type="XXXX">
                    found_any_condition = True
                    condition_category = _condition.get('type')
                    if condition_category == 'Condition':
                        criteria_xml = _condition.object.get('criteria_xml')
                        criteria_xml = criteria_xml.replace('\n', '')
                        field = _condition.object.get('field')
                        group = _condition.object.get('group')
                        operator = _condition.object.get('operator')
                        value = _condition.object.get('value')
                        version = _condition.object.get('version')
                        criteria_xml_plain = base64.b64decode(criteria_xml)


                        # Grab operation and field name from criteria_xml
                        #
                        field_from_criteria = {'is_found': 0, 'value': ''}
                        operator_from_criteria = {'is_found': 0, 'value': ''}
                        soap_criteria = BeautifulSoup(criteria_xml_plain)

                        for element in soap_criteria.i:
                            if element.name == 's' and element.get_text() == 'ft':
                                field_from_criteria['is_found'] = 1
                                continue

                            if field_from_criteria['is_found'] == 1 and element.name == 'u':
                                field_from_criteria['value'] = element.get_text()
                                field_from_criteria['is_found'] = 2
                                continue

                            if element.name == 's' and element.get_text() == 'op':
                                operator_from_criteria['is_found'] = 1
                                continue

                            if operator_from_criteria['is_found'] == 1 and element.name == 'i':
                                operator_from_criteria['value'] = element.get_text()
                                operator_from_criteria['is_found'] = 2
                                continue

                        #
                        # end grab operation and field name from criteria_xml
                        xplan_item = XPlanItem()
                        xplan_item.set_d_object_name(object_name)
                        xplan_item.set_d_condition_type(pos)
                        xplan_item.set_d_action_field(field_from_criteria['value'])
                        xplan_item.set_d_operation(int(operator_from_criteria['value']))
                        xplan_item.set_d_value(criteria_xml_plain)
                        xplan_item.set_d_reference(reference)

                        xplan_item.set_x_object_type(object_type['value'])
                        xplan_item.set_x_condition_category(condition_category)
                        xplan_item.set_x_value_in_base64(criteria_xml)
                        xplan_item.set_x_field(field)
                        xplan_item.set_x_group(group)
                        xplan_item.set_x_operator(operator)
                        xplan_item.set_x_version(version)

                        self.xplan_object.append_item(xplan_item)

                    elif condition_category == 'FieldConditionStore':
                        field = _condition.object.get('field')
                        operator_value = _condition.object.get('operator_value')
                        value_xml = _condition.object.get('value_xml')
                        value_xml = value_xml.replace('\n', '')
                        version = _condition.object.get('version')
                        value_xml_plain = base64.b64decode(value_xml)

                        xplan_item = XPlanItem()
                        xplan_item.set_x_object_type(object_type['value'])
                        xplan_item.set_d_object_name(object_name)
                        xplan_item.set_d_condition_type(pos)
                        xplan_item.set_d_action_field(field)
                        xplan_item.set_d_operation(int(operator_value))
                        xplan_item.set_d_value(value_xml_plain)
                        xplan_item.set_d_reference(reference)

                        xplan_item.set_x_condition_category(condition_category)
                        xplan_item.set_x_value_in_base64(value_xml)
                        xplan_item.set_x_field(field)
                        xplan_item.set_x_version(version)

                        self.xplan_object.append_item(xplan_item)

                    else:
                        print '____________unknown type____________'

                pos = pos + 1

            if not found_any_condition:
                xplan_item = XPlanItem()
                xplan_item.set_d_object_name(object_name)
                xplan_item.set_d_reference(reference)

                xplan_item.set_x_object_type(object_type['value'])

                self.xplan_object.append_item(xplan_item)

    def get_xplan_object(self):
        return self.xplan_object

    def generate_obj_file(self):
        print 'Saving object file...'
        name = os.path.splitext(os.path.basename(self.filename))[0]
        f = open(name + '_obj.xml', 'w')
        f.write(self.get_xml())
        f.close()

    def get_xml(self):
        return self.soup.prettify()

    def print_xml(self):
        print self.get_xml()

    def print_xplan_object(self):
        for i in self.get_xplan_object().get_obj():
            print i.get_item()

    def get_filename(self):
        return self.filename

    def __clear_conditions(self, soap_node):
        #<object type="List">
        #</object>
        #<object type="List">
        #</object>
        #<object type="List">
        #</object>
        #<object type="List">
        #</object>
        #<object type="List">
        #</object>

        soap_node.clear()

        for i in range(0, 5):
            object_type = self.soup.new_tag("object")
            object_type['type'] = "List"
            soap_node.append(object_type)

    def get_FieldConditionStore(self, data):
        #<object type="FieldConditionStore">
        #    <object field="%s" operator_value="%s" value_xml="%s" version="%s">
        #    </object>
        #</object>
        object_type = self.soup.new_tag("object")
        object_type['type'] = "FieldConditionStore"

        object_field = self.soup.new_tag("object")
        object_field['field'] = data['x_field']
        object_field['operator_value'] = str(data['d_operation'])
        object_field['value_xml'] = data['x_value_in_base64']
        object_field['version'] = data['x_version']

        object_type.append(object_field)

        return object_type


    def get_Condition(self, data):
        #<object type="Condition">
        #    <object criteria_xml="%s" field="%s" group="%s" operator="%s" store_mode="xmlised" value="" version="%s">
        #    <extended_value type="String" value=""/></object>
        #</object>

        object_type = self.soup.new_tag("object")
        object_type['type'] = "Condition"

        object_field = self.soup.new_tag("object")
        object_field['criteria_xml'] = data['x_value_in_base64']
        object_field['field'] = data['x_field']
        object_field['group'] = data['x_group']
        object_field['operator'] = data['x_operator']
        object_field['value'] = ""
        object_field['version'] = data['x_version']

        object_type.append(object_field)

        return object_type