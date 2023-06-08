""" 
Description: 
  Divides sales data CSV file into individual order data Excel files.

Usage:
  python process_sales_data.py sales_csv_path

Parameters:
  sales_csv_path = Full path of the sales data CSV file
"""
import re
import pandas as pd
import sys
import os.path
from datetime import  date

def main():
    sales_csv_path = get_sales_csv_path()
    orders_dir_path = create_orders_dir(sales_csv_path)
    process_sales_data(sales_csv_path, orders_dir_path)

def get_sales_csv_path():
    """Gets the path of sales data CSV file from the command line

    Returns:
        str: Path of sales data CSV file
    """
    # T Check whether command line parameter provided
    num_params = len(sys.argv) -1
    if num_params < 1:
        print("Error:Missing CSV path parameter.")
        sys.exit()

    # Check whether provide parameter is valid path of file
    csv_path = sys.argv[1]
    if not os.path.isfile(csv_path):
        print("Error: CSV path is not existing file.")
        sys.exit()

    #  Return path of sales data CSV file
    return os.path.abspath(csv_path)

def create_orders_dir(sales_csv_path):
    """Creates the directory to hold the individual order Excel sheets

    Args:
        sales_csv_path (str): Path of sales data CSV file

    Returns:
        str: Path of orders directory
    """
    #  Get directory in which sales data CSV file resides
    sales_csv_dir = os.path.dirname(sales_csv_path)


    #  Determine the path of the directory to hold the order data files
    todays_date = date.today().isoformat()
    orders_dir = f'Orders_{todays_date}'
    orders_dir_path = os.path.join(sales_csv_dir,orders_dir)

    #  Create the orders directory if it does not already exist
    if not os.path.isdir(orders_dir_path):
        os.makedirs(orders_dir_path)
    #  Return path of orders directory
    return orders_dir_path

def process_sales_data(sales_csv_path, orders_dir_path):
    """Splits the sales data into individual orders and save to Excel sheets

    Args:
        sales_csv_path (str): Path of sales data CSV file
        orders_dir_path (str): Path of orders directory
    """
    #  Import the sales data from the CSV file into a DataFrame
    df = pd.read_csv(sales_csv_path)

    #  Insert a new "TOTAL PRICE" column into the DataFrame
    df.insert(7,'TOTAL PRICE', df['ITEM QUANTITY'] * df['ITEM PRICE'])
    # Remove columns from the DataFrame that are not needed
    df.drop(columns=['ADDRESS','CITY', 'STATE', 'POSTAL CODE', 'COUNTRY'], inplace=True)
    #  Groups orders by ID and iterate 
    for order_id, order_df in df.groupby('ORDER ID'):
        #  Remove the 'ORDER ID' column
        order_df.drop(columns=['ORDER ID'], inplace=True)
        # Sort the items by item number
        order_df.sort_values(by='ITEM NUMBER', inplace=True)
        # Append a "GRAND TOTAL" row
        grand_total = order_df['TOTAL PRICE'].sum()
        grand_total_df = pd.DataFrame({'ITEM PRICE': ['GRAND TOTAL'], 'TOTAL PRICE': [grand_total]})
        order_df = pd.concat([order_df, grand_total_df])
        
     
        #  Determine the file name and full path of the Excel sheet
        customer_name = order_df['CUSTOMER NAME'].values[0]
        customer_name = re.sub(r'\w', '', customer_name)
        order_file = f'Order{order_id}_{customer_name}.xlsx'
        order_excel_path = os.path.join(orders_dir_path, order_file)
        #  Export the data to an Excel sheet
        worksheet_name = f'Order #{order_id}'
        #order_df.to_excel(order_excel_path, index=False, sheet_name=worksheet_name)

 # Format the Excel sheet

        writer = pd.ExcelWriter("order_file.xlsx", engine="xlsxwriter")
        df.to_excel(writer, sheet_name="worksheet_name")

        workbook = writer.book
        worksheet = writer.sheets["worksheet_name"]

 #  Define format for the money columns
    format1 = workbook.add_format({"num_format": "#/#/####"})
    format2 = workbook.add_format({"num_format": "#"})
    format3 = workbook.add_format({"num_format": "xxxxxxxx xxxx"})
    format4 = workbook.add_format({"num_format":"X##_####"})
    format5 = workbook.add_format({"num_format":"##"})
    format6 = workbook.add_format({"num_format":"$#,###"})
    format7 = workbook.add_format({"num_format":"$#,###.00"})
    format8 = workbook.add_format({"num_format":"Xxxxxxx"})
    format9 = workbook.add_format({"num_format":"Xxxxxx xxxxxxx xxxxxxxx Xx"})

 #  Format each colunm
    worksheet.set_column(1, 1, 11, format1)
    worksheet.set_column(2, 2, 13, format2)
    worksheet.set_column(3, 3, 15, format4)
    worksheet.set_column(4, 4, 15, format5)
    worksheet.set_column(5, 5, 15, format6)
    worksheet.set_column(6, 6, 13, format6)
    worksheet.set_column(7, 7, 13, format7)
    worksheet.set_column(8, 8, 10, format8)
    worksheet.set_column(9, 9, 30, format9)

 #  Close the Excelwriter

    writer.close()

    return

if __name__ == '__main__':
    main()