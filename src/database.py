from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import bcrypt

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    lancamentos = relationship('Lancamento', back_populates='user', cascade='all, delete-orphan')
    orcamentos = relationship('Orcamento', back_populates='user', cascade='all, delete-orphan')


class Lancamento(Base):
    __tablename__ = 'lancamentos'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    data = Column(DateTime, nullable=False)
    tipo = Column(String(20), nullable=False)
    categoria = Column(String(100), nullable=False)
    cliente_fornecedor = Column(String(200))
    descricao = Column(String(500))
    conta = Column(String(50), nullable=False)
    valor = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship('User', back_populates='lancamentos')


class Orcamento(Base):
    __tablename__ = 'orcamentos'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    categoria = Column(String(100), nullable=False)
    limite = Column(Float, nullable=False)
    mes = Column(String(7), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship('User', back_populates='orcamentos')


engine = create_engine('sqlite:///organiza_caixa.db', echo=False)
Session = sessionmaker(bind=engine)


def init_db():
    Base.metadata.create_all(engine)


def create_user(username: str, password: str) -> User:
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    session = Session()
    user = User(username=username, password_hash=password_hash.decode('utf-8'))
    session.add(user)
    session.commit()
    session.close()
    return user


def get_user(username: str) -> User | None:
    session = Session()
    user = session.query(User).filter(User.username == username).first()
    session.close()
    return user


def get_user_by_id(user_id: int) -> User | None:
    session = Session()
    user = session.query(User).filter(User.id == user_id).first()
    session.close()
    return user


def verify_password(user: User, password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8'))


def save_lancamento(
    user_id: int,
    data: datetime,
    tipo: str,
    categoria: str,
    cliente_fornecedor: str | None,
    descricao: str | None,
    conta: str,
    valor: float
) -> Lancamento:
    session = Session()
    lancamento = Lancamento(
        user_id=user_id,
        data=data,
        tipo=tipo,
        categoria=categoria,
        cliente_fornecedor=cliente_fornecedor or '',
        descricao=descricao or '',
        conta=conta,
        valor=valor
    )
    session.add(lancamento)
    session.commit()
    session.close()
    return lancamento


def get_lancamentos(user_id: int, conta: str | None = None) -> list[Lancamento]:
    session = Session()
    query = session.query(Lancamento).filter(Lancamento.user_id == user_id)
    if conta and conta != 'Todas':
        query = query.filter(Lancamento.conta == conta)
    lancamentos = query.order_by(Lancamento.data.desc()).all()
    session.close()
    return lancamentos


def delete_lancamento(lancamento_id: int, user_id: int):
    session = Session()
    session.query(Lancamento).filter(
        Lancamento.id == lancamento_id,
        Lancamento.user_id == user_id
    ).delete()
    session.commit()
    session.close()


def delete_all_lancamentos(user_id: int, conta: str | None = None):
    session = Session()
    query = session.query(Lancamento).filter(Lancamento.user_id == user_id)
    if conta and conta != 'Todas':
        query = query.filter(Lancamento.conta == conta)
    query.delete()
    session.commit()
    session.close()


def save_orcamento(user_id: int, categoria: str, limite: float, mes: str):
    session = Session()
    existing = session.query(Orcamento).filter(
        Orcamento.user_id == user_id,
        Orcamento.categoria == categoria,
        Orcamento.mes == mes
    ).first()
    
    if existing:
        existing.limite = limite
    else:
        orcamento = Orcamento(user_id=user_id, categoria=categoria, limite=limite, mes=mes)
        session.add(orcamento)
    
    session.commit()
    session.close()


def get_orcamentos(user_id: int, mes: str) -> list[Orcamento]:
    session = Session()
    orcamentos = session.query(Orcamento).filter(
        Orcamento.user_id == user_id,
        Orcamento.mes == mes
    ).all()
    session.close()
    return orcamentos
