import base64

import xlsxwriter
import xlrd

from xplan import Operation, SubPageCondition, OtherCondition, XPlanObject, XPlanItem


class Icon:
    def __init__(self):
        self.icons = {'Title': 'icons/title.png',
                      'Gap': 'icons/gap.png',
                      'Text': 'icons/text.png',
                      'Field': 'icons/field.png',
                      'SubPage': 'icons/page.png',
                      'Group': 'icons/group.png',
                      'Xplan': 'icons/xplan.png',
                      'Newspeedgroup': 'icons/newspeedgroup.png',
                      'Speedgroup': 'icons/speedgroup.png',
                      'IFrame': 'icons/iframe.png',
                      'Xtool': 'icons/xtool.png',
        }

    def get_path(self, name):
        try:
            return self.icons[name]
        except:
            return ''


class Excel:
    def __init__(self):
        self.filename = 'page.xls'
        self.icon = Icon()
        self.subpagecondition = SubPageCondition()
        self.othercondition = OtherCondition()
        self.operation = Operation()
        self.ICON_COLUMN_NUM = 0
        self.OBJECT_NAME_COLUMN_NUM = 1
        self.OBJECT_TYPE_COLUMN_NUM = 2
        self.ACTION_FIELD_COLUMN_NUM = 3
        self.OPERATION_COLUMN_NUM = 4
        self.VALUE_COLUMN_NUM = 5
        self.KEY_COLUMN_NUM = 6
        self.ORI_OBJ_COLUMN_NUM = 7


    def __set_operation_column(self, row_pos, object_type, worksheet):
        if object_type != 'SubPage':
            worksheet.data_validation(row_pos, self.OPERATION_COLUMN_NUM, row_pos, self.OPERATION_COLUMN_NUM,
                                      {'validate': 'list',
                                       'source': self.operation.get_names()})


    def __set_object_type(self, row_pos, object_type, worksheet):
        if object_type == 'SubPage':
            worksheet.data_validation(row_pos, self.OBJECT_TYPE_COLUMN_NUM, row_pos, self.OBJECT_TYPE_COLUMN_NUM,
                                      {'validate': 'list',
                                       'source': self.subpagecondition.get_names()})
        else:
            worksheet.data_validation(row_pos, self.OBJECT_TYPE_COLUMN_NUM, row_pos, self.OBJECT_TYPE_COLUMN_NUM,
                                      {'validate': 'list',
                                       'source': self.othercondition.get_names()})

    def generate_xls_file(self, xplan_object):
        print 'Generating excel file...'
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

        worksheet.write('A1', '', header_format)
        worksheet.write('B1', 'Object Name', header_format)
        worksheet.write('C1', 'Condition Type', header_format)
        worksheet.write('D1', 'Action Field', header_format)
        worksheet.write('E1', 'Operation', header_format)
        worksheet.write('F1', 'Value', header_format)
        worksheet.write('G1', 'Reference', header_format)

        worksheet.set_column('A:A', 2) #Object name column width
        worksheet.set_column('B:B', 110) #Object name column width
        worksheet.set_column('C:C', 25) #Condition type column width
        worksheet.set_column('D:D', 30) #Action Field column width
        worksheet.set_column('E:E', 15) #Operator column width
        worksheet.set_column('F:F', 100) #Value column width
        worksheet.set_column('G:G', 15) #key column width

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

            worksheet.write(rows, self.OBJECT_NAME_COLUMN_NUM, item['d_object_name'], alternate_color)
            self.__set_object_type(rows, object_type, worksheet)
            self.__set_operation_column(rows, object_type, worksheet) # Generate drop down

            condition_type = item['x_condition_category']
            if condition_type:

                if condition_type == 'FieldConditionStore':
                    worksheet.write(rows, self.OBJECT_TYPE_COLUMN_NUM,
                                    self.othercondition.get_name(item['d_condition_type']), alternate_color)
                    worksheet.write(rows, self.OPERATION_COLUMN_NUM, self.operation.get_name(item['d_operation']),
                                    alternate_color)
                    worksheet.write(rows, self.ACTION_FIELD_COLUMN_NUM, item['d_action_field'], alternate_color)
                elif condition_type == 'Condition':
                    worksheet.write(rows, self.OBJECT_TYPE_COLUMN_NUM,
                                    self.subpagecondition.get_name(item['d_condition_type']), alternate_color)
                    worksheet.write(rows, self.OPERATION_COLUMN_NUM, self.operation.get_name(item['d_operation']),
                                    locked)
                    worksheet.write(rows, self.ACTION_FIELD_COLUMN_NUM, item['d_action_field'], locked)
                worksheet.write(rows, self.VALUE_COLUMN_NUM, item['d_value'], alternate_color)

            worksheet.write(rows, self.KEY_COLUMN_NUM, reference, locked_shrink)
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

            j = 1
            column_data = {}
            for column in row:
                if j == 1:
                    xplan_item.set_d_object_name(column.value)
                elif j == 2:
                    column_data['condition_type'] = column.value
                elif j == 3:
                    column_data['action_field'] = column.value
                elif j == 4:
                    column_data['operation'] = column.value
                elif j == 5:
                    column_data['value'] = column.value
                elif j == 6:
                    column_data['reference'] = column.value
                    #elif j == 7:
                #    column_data['original_object'] = column.value

                j = j + 1
            column_data['operation_value'] = self.operation.get_value(column_data['operation'])
            column_data['base64data'] = base64.b64encode(column_data['value'])
            g_obj.append(column_data)
        return g_obj