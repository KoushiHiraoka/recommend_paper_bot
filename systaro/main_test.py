import datetime 

def main():
    year = range(datetime.date.today().year-2,
                 datetime.date.today().year)
    
    print(year)
if __name__ == "__main__":

    main()