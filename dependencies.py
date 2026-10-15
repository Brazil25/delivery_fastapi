from models import db, Usuario
from sqlalchemy.orm import sessionmaker, Session
from fastapi import Depends, HTTPException
from jose import jwt, JWTError
from config import SECRET_KEY, ALGORITHM, oauth2_schema

def pegar_sessao():
    try:
        Session = sessionmaker(bind=db)
        session = Session()
        yield session
    finally:
        session.close()

def verificar_token(token: str = Depends(oauth2_schema), session: Session=Depends(pegar_sessao)):
    try:
        dic_info = jwt.decode(token, SECRET_KEY, [ALGORITHM])
        id_usuario = int(dic_info.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="Acesso Negado, verifique a validade do token")
    usuario = session.query(Usuario).filter(Usuario.id==id_usuario).first()
    if not usuario:
        raise HTTPException(status_code=401, detail="Acesso Inválido")
    return usuario

def verificar_admin(usuario: Usuario = Depends(verificar_token)):
    if not usuario.admin:
        raise HTTPException(
            status_code=403, 
            detail="Acesso negado: Apenas administradores podem realizar esta operação"
        )
    return usuario