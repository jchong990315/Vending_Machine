from sqlalchemy import create_engine


def get_engine():
    # need this for live updates
    return create_engine("mysql+pymysql://root:Group17@project_17-db8-1:3306/Vending_Machine")
