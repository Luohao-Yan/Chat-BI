from sqlalchemy import Column, Integer, String, Float, Date, SmallInteger, TIMESTAMP, text
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2 import Geometry

Base = declarative_base()

class PlMobilePeopleFlowData(Base):
    __tablename__ = 'pl_mobile_people_flow_data'
    id = Column(Integer, primary_key=True, autoincrement=True)
    all_count = Column(Integer, comment='高新区日人流量')
    in_count = Column(Integer, comment='进高新区')
    out_count = Column(Integer, comment='出高新区')
    statistics_date = Column(Date, comment='统计日期')
    activation = Column(Float, default=0, comment='活跃度')
    base_line_value = Column(Float, default=0, comment='活跃度基线值')

class MobileDayFlowTag(Base):
    __tablename__ = 'mobile_day_flow_tag'
    id = Column(Integer, primary_key=True, autoincrement=True)
    area = Column(String(50))
    label_cnt = Column(Integer, comment='人数')
    tag = Column(String(50), comment='标签类别，例如省外来源，省内来源，性别，年龄等')
    label = Column(String(50), comment='标签名称，例如标签类别为省内来源时，标签名称为“珠海”')
    type = Column(SmallInteger, comment='1=日驻留、2=新流入、3=新流出')
    day = Column(String(10))
    create_time = Column(TIMESTAMP, server_default=text('now()'))

class PlPopTrendOfEndYear(Base):
    __tablename__ = 'pl_pop_trend_of_end_year'
    date_time = Column(String(10), primary_key=True)
    num = Column(Float, comment='单位(万)')
    create_time = Column(TIMESTAMP, server_default=text('now()'))

class GridFirstLevelInfo(Base):
    __tablename__ = 'grid_first_level_info'
    community = Column(String(30), primary_key=True, comment='社区')
    grid_leader = Column(String(1000), comment='网格长信息')
    build_num = Column(Integer, default=0, comment='楼栋数')
    population = Column(Integer, default=0, comment='人数')
    inconvenience_num = Column(Integer, default=0, comment='行动不便人数')
    disable_num = Column(Integer, default=0, comment='残疾人人数')
    other_pop_num = Column(Integer, default=0, comment='港澳台外籍人数')
    geom = Column(Geometry, comment='地理信息')
    overview = Column(String(500), comment='概况')
    area = Column(Float, comment='社区面积（平方公里）')
    resident_population = Column(Integer, comment='常住人口')
    registered_population = Column(Integer, comment='户籍人口')
    total_population = Column(Integer, comment='总居住人口')
    location = Column(String(50), comment='中心坐标')
    mac = Column(String(255), comment='grid_leader字段的mac值')