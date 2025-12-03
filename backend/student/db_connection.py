import pyodbc as odbc


#this is a database library

class database():

  Driver_name = "ODBC Driver 18 for SQL Server"
  Server_name = "Alvy\SQLEXPRESS"
  Database_name = "library"
  # Define your connection string
  # Replace 'your_server_name', 'your_database_name' with your actual values.
  # If using Windows Authentication (Integrated Security), you can use Trusted_Connection=yes.
  # If using SQL Server Authentication, replace uid and pwd with your username and password.
  connection_string = f"""
      DRIVER={{{Driver_name}}};
      SERVER={Server_name};
      DATABASE={Database_name};
      Trusted_Connection=yes;
      TrustServerCertificate=yes;
  """
  
  

  def connect():
    return odbc.connect(database.connection_string)

