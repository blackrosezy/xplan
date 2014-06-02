import cPickle as pickle
import base64
import os, logging

import xlsxwriter
import xlrd

from xplan import Operation, SubPageCondition, OtherCondition, XPlanObject, XPlanItem
from util import Util

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s') # include timestamp

class Icon:
    def __init__(self):
        self.icons = {'Title': Util.resource_path(os.path.join('images', 'title.png')),
                      'Gap': Util.resource_path(os.path.join('images', 'gap.png')),
                      'Text': Util.resource_path(os.path.join('images', 'text.png')),
                      'Field': Util.resource_path(os.path.join('images', 'field.png')),
                      'SubPage': Util.resource_path(os.path.join('images', 'page.png')),
                      'Group': Util.resource_path(os.path.join('images', 'group.png')),
                      'Xplan': Util.resource_path(os.path.join('images', 'xplan.png')),
                      'Newspeedgroup': Util.resource_path(os.path.join('images', 'newspeedgroup.png')),
                      'Speedgroup': Util.resource_path(os.path.join('images', 'speedgroup.png')),
                      'IFrame': Util.resource_path(os.path.join('images', 'iframe.png')),
                      'Xtool': Util.resource_path(os.path.join('images', 'xtool.png')),
        }

    def get_path(self, name):
        try:
            return self.icons[name]
        except:
            logging.warning('[info] unknown icon of ' + name)
            return Util.resource_path(os.path.join('images', 'unknown.png'))


class Excel:
    def __init__(self):
        self.filename = 'page.xls'
        self.icon = Icon()
        self.subpagecondition = SubPageCondition()
        self.othercondition = OtherCondition()
        self.operation = Operation()
        self.INCLUDE_COLUMN_NUM = 0
        self.ICON_COLUMN_NUM = 1
        self.OBJECT_NAME_COLUMN_NUM = 2
        self.CONDITION_TYPE_COLUMN_NUM = 3
        self.ACTION_FIELD_COLUMN_NUM = 4
        self.OPERATION_COLUMN_NUM = 5
        self.VALUE_COLUMN_NUM = 6
        self.KEY_COLUMN_NUM = 7
        self.ORI_OBJ_COLUMN_NUM = 8
        self.INCLUDE_SYMBOL = '*'


    def __set_operation_column(self, row_pos, object_type, worksheet):
        if object_type != 'SubPage':
            worksheet.data_validation(row_pos, self.OPERATION_COLUMN_NUM, row_pos, self.OPERATION_COLUMN_NUM,
                                      {'validate': 'list',
                                       'source': self.operation.get_names()})


    def __set_object_type(self, row_pos, object_type, worksheet):
        if object_type == 'SubPage':
            worksheet.data_validation(row_pos, self.CONDITION_TYPE_COLUMN_NUM, row_pos, self.CONDITION_TYPE_COLUMN_NUM,
                                      {'validate': 'list',
                                       'source': self.subpagecondition.get_names()})
        else:
            worksheet.data_validation(row_pos, self.CONDITION_TYPE_COLUMN_NUM, row_pos, self.CONDITION_TYPE_COLUMN_NUM,
                                      {'validate': 'list',
                                       'source': self.othercondition.get_names()})

    def generate_xls_file(self, xplan_object):
        logging.info('Generating excel file...')
        workbook = xlsxwriter.Workbook(self.filename, {'constant_memory': True})
        worksheet = workbook.add_worksheet()

        wrap_format = workbook.add_format()
        wrap_format.set_text_wrap()

        merge_format = workbook.add_format({'align': 'center'})

        small_font_format = workbook.add_format()
        small_font_format.set_font_size(9)

        header_format = workbook.add_format()
        header_format.set_bg_color('#C5D9F1')

        color_1_format = workbook.add_format()
        color_1_format.set_bg_color('#D8E4BC')
        color_1_format.set_font_size(9)

        color_2_format = workbook.add_format()
        color_2_format.set_bg_color('#F2F2F2')
        color_2_format.set_font_size(9)

        locked = workbook.add_format()
        locked.set_bg_color('#BDC3C7')
        locked.set_font_size(9)

        locked_shrink = workbook.add_format()
        locked_shrink.set_bg_color('#BDC3C7')
        locked_shrink.set_shrink()

        worksheet.write(0, self.INCLUDE_COLUMN_NUM, 'Inc.', header_format)
        worksheet.write(0, self.ICON_COLUMN_NUM, '', header_format)
        worksheet.write(0, self.OBJECT_NAME_COLUMN_NUM, 'Object Name', header_format)
        worksheet.write(0, self.CONDITION_TYPE_COLUMN_NUM, 'Condition Type', header_format)
        worksheet.write(0, self.ACTION_FIELD_COLUMN_NUM, 'Action Field', header_format)
        worksheet.write(0, self.OPERATION_COLUMN_NUM, 'Operation', header_format)
        worksheet.write(0, self.VALUE_COLUMN_NUM, 'Value', header_format)
        worksheet.write(0, self.KEY_COLUMN_NUM, 'Reference', header_format)

        worksheet.set_column(self.INCLUDE_COLUMN_NUM, self.INCLUDE_COLUMN_NUM, 3) #export column width
        worksheet.set_column(self.ICON_COLUMN_NUM, self.ICON_COLUMN_NUM, 2) #Icon column width
        worksheet.set_column(self.OBJECT_NAME_COLUMN_NUM, self.OBJECT_NAME_COLUMN_NUM, 110) #Object name column width
        worksheet.set_column(self.CONDITION_TYPE_COLUMN_NUM, self.CONDITION_TYPE_COLUMN_NUM,
                             25) #Condition type column width
        worksheet.set_column(self.ACTION_FIELD_COLUMN_NUM, self.ACTION_FIELD_COLUMN_NUM, 30) #Action Field column width
        worksheet.set_column(self.OPERATION_COLUMN_NUM, self.OPERATION_COLUMN_NUM, 15) #Operation column width
        worksheet.set_column(self.VALUE_COLUMN_NUM, self.VALUE_COLUMN_NUM, 100) #Value column width
        worksheet.set_column(self.KEY_COLUMN_NUM, self.KEY_COLUMN_NUM, 15) #key column width

        worksheet.autofilter('B1:B1')
        worksheet.freeze_panes(1, 0)

        rows = 1
        alternate_color = color_1_format
        previous_reference = ''
        for object in xplan_object.get_obj():
            item = object.get_item()
            object_type = item['x_object_type']
            reference = item['d_reference']

            if reference != previous_reference:
                worksheet.insert_image(rows, self.ICON_COLUMN_NUM, self.icon.get_path(object_type))
                previous_reference = reference

            worksheet.data_validation(rows, self.INCLUDE_COLUMN_NUM, rows, self.INCLUDE_COLUMN_NUM,
                                      {'validate': 'list',
                                       'source': [self.INCLUDE_SYMBOL, '']})
            worksheet.write(rows, self.INCLUDE_COLUMN_NUM, '')

            worksheet.write(rows, self.OBJECT_NAME_COLUMN_NUM, item['d_object_name'], alternate_color)
            self.__set_object_type(rows, object_type, worksheet)
            self.__set_operation_column(rows, object_type, worksheet) # Generate drop down

            condition_category = item['x_condition_category']
            if condition_category:

                if condition_category == 'FieldConditionStore':
                    worksheet.write(rows, self.CONDITION_TYPE_COLUMN_NUM,
                                    self.othercondition.get_name(item['d_condition_type']), alternate_color)
                    worksheet.write(rows, self.OPERATION_COLUMN_NUM, self.operation.get_name(item['d_operation']),
                                    alternate_color)
                    worksheet.write(rows, self.ACTION_FIELD_COLUMN_NUM, item['d_action_field'], alternate_color)
                elif condition_category == 'Condition':
                    worksheet.write(rows, self.CONDITION_TYPE_COLUMN_NUM,
                                    self.subpagecondition.get_name(item['d_condition_type']), alternate_color)
                    worksheet.write(rows, self.OPERATION_COLUMN_NUM, self.operation.get_name(item['d_operation']),
                                    locked)
                    worksheet.write(rows, self.ACTION_FIELD_COLUMN_NUM, item['d_action_field'], locked)
                worksheet.write(rows, self.VALUE_COLUMN_NUM, item['d_value'], alternate_color)

            worksheet.write(rows, self.KEY_COLUMN_NUM, base64.b64encode(pickle.dumps(item)), locked_shrink)
            rows = rows + 1

            if alternate_color == color_1_format:
                alternate_color = color_2_format
            else:
                alternate_color = color_1_format

    def get_xplan_object(self):
        xplan_object = XPlanObject()
        workbook = xlrd.open_workbook(self.filename)
        worksheet = workbook.sheet_by_name('Sheet1')

        skip_first_row = True
        for i in range(worksheet.nrows):

            if skip_first_row: #skip first row (header)
                skip_first_row = False
                continue

            row = worksheet.row(i)
            xplan_item = XPlanItem()

            j = 0
            include_row = False
            for column in row:
                if j == self.INCLUDE_COLUMN_NUM:
                    if column.value.strip() == self.INCLUDE_SYMBOL:
                        include_row = True
                if j == self.OBJECT_NAME_COLUMN_NUM:
                    xplan_item.set_d_object_name(column.value)
                elif j == self.CONDITION_TYPE_COLUMN_NUM:
                    xplan_item.set_d_condition_type(column.value) #temporary assign
                elif j == self.ACTION_FIELD_COLUMN_NUM:
                    xplan_item.set_d_action_field(column.value)
                elif j == self.OPERATION_COLUMN_NUM:
                    xplan_item.set_d_operation(column.value) #temporary assign
                elif j == self.VALUE_COLUMN_NUM:
                    xplan_item.set_d_value(column.value)
                elif j == self.KEY_COLUMN_NUM:
                    # original data
                    original_data = pickle.loads(base64.b64decode(column.value))

                    # new data from column 2 to 6
                    new_data = xplan_item.get_item()

                    # update 'd_condition_type' to int
                    object_type = original_data['x_object_type']
                    if object_type == 'SubPage':
                        val = self.subpagecondition.get_value(new_data['d_condition_type'])
                        xplan_item.set_d_condition_type(val)
                    else:
                        val = self.othercondition.get_value(new_data['d_condition_type'])
                        xplan_item.set_d_condition_type(val)

                    # update 'd_operation' to int
                    val = self.operation.get_value(new_data['d_operation'])
                    xplan_item.set_d_operation(val)

                    # set reference
                    xplan_item.set_d_reference(original_data['d_reference'])

                    #  encode new base64 value
                    val = base64.b64encode(new_data['d_value'])
                    xplan_item.set_x_value_in_base64(val)

                    #  set object type
                    object_type = original_data['x_object_type']
                    xplan_item.set_x_object_type(object_type)

                    #  set condition category (guess??)
                    condition_category = original_data['x_condition_category']
                    if object_type == 'SubPage' and condition_category == '':
                        condition_category = 'Condition'
                    elif object_type != 'SubPage' and condition_category == '':
                        condition_category = 'FieldConditionStore'

                    xplan_item.set_x_condition_category(condition_category)

                    #  set other fields
                    xplan_item.set_x_field(original_data['x_field'])
                    xplan_item.set_x_group(original_data['x_group'])
                    xplan_item.set_x_operator(original_data['x_operator'])
                    xplan_item.set_x_version(original_data['x_version'])
                    xplan_item.set_x_condition_unique_id(original_data['x_condition_unique_id'])
                j = j + 1

            if include_row:
                xplan_object.append_item(xplan_item)

        return xplan_object