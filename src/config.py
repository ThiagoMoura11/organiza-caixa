from dataclasses import dataclass
from typing import Literal

CONTAS = ['Itau', 'Inter']

CATEGORIAS = [
    'Seguro',
    'Parcela compra',
    'Aluguel',
    'Custo empresa',
    'Itau',
    'Cartão de Crédito',
    'Reembolso',
    'Pedagio',
    'Financiamento',
    'Pessoal',
    'Tarifa Bancaria',
    'Imposto',
    'Despesa Extra',
    'Salario',
    'Abastecimento',
    'Manutenção',
    'Contabilidade',
    'Rastreador',
    'Recebimento Aplicação',
    'Operação amonex',
    'Operação LOG',
    'Velada - Brasil Web',
    'Frete',
    'Transferência',
    'Sem categoria',
]

TIPO_LANCAMENTO = ['Entrada', 'Saída']

@dataclass
class Colunas:
    DATA = 'Data'
    TIPO = 'Tipo'
    CATEGORIA = 'Categoria'
    CLIENTE_FORNECEDOR = 'Cliente/Fornecedor'
    DESCRICAO = 'Descrição'
    CONTA = 'Conta'
    VALOR = 'Valor'

COLUNAS = Colunas()
