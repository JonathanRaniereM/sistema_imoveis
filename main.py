import sys
import mysql.connector
from PyQt5 import QtCore, QtGui, QtWidgets

from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget,
                             QLabel, QInputDialog, QListWidget, QHBoxLayout, QStackedWidget,
                             QListWidgetItem, QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView,
                             QCalendarWidget, QDialog, QDialogButtonBox,QGridLayout)

from PyQt5.QtGui import QBrush, QColor,QLinearGradient,QIcon
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont
from datetime import datetime
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QListWidget, QListWidgetItem, QLabel, QToolBar, QAction, QMenu, QMenuBar, QTableWidget, QTableWidgetItem, QHeaderView, QComboBox, QLineEdit, QCalendarWidget, QMessageBox, QGridLayout
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QComboBox
import resources


def conectar_mysql():
        try:
            conn = mysql.connector.connect(
                host='localhost',
                user='controle',
                password='123456',
                database='controle_gastos',
                auth_plugin='mysql_native_password',
                use_pure=True,
                client_flags=[mysql.connector.ClientFlag.LOCAL_FILES]
            )
            return conn
        except mysql.connector.Error as e:
            print(f"Erro ao conectar ao banco de dados: {e}")
            return None
def criar_tabelas_mysql(conn):
    cursor = conn.cursor()

    # Tabela de imóveis
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS imoveis (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(255) NOT NULL
        )
    ''')

    # Tabela de itens
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS itens (
            id INT AUTO_INCREMENT PRIMARY KEY,
            item VARCHAR(255) NOT NULL,
            quantidade VARCHAR(255) NOT NULL,
            forma_pg VARCHAR(255) NOT NULL,
            valor DECIMAL(10, 2) NOT NULL,
            data DATE NOT NULL,  # Altere o tipo de dado para DATE
            id_imovel INT,
            FOREIGN KEY (id_imovel) REFERENCES imoveis (id)
        )
    ''')

    conn.commit()

class Imovel:
    def __init__(self, nome):
        self.nome = nome
        self.gastos = []

    def adicionar_gasto(self, item, forma_pagamento, valor, data):
        
        id_imovel = self.obter_id_imovel(self.nome)
        if id_imovel is not None:
            conn = conectar_mysql()
            if conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO itens (item, forma_pg, valor, data, id_imovel)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (item, forma_pagamento, valor, data, id_imovel))
                conn.commit()
                conn.close()

    def obter_id_imovel(self, nome_imovel):
        conn = conectar_mysql()
        if conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM imoveis WHERE nome = %s', (nome_imovel,))
            result = cursor.fetchone()
            conn.close()
            if result:
                return result[0]  # Retorna o ID encontrado
        return None  # Retorna None se o imóvel não for encontrado

    def total_gastos(self):
        return sum(valor for item, valor, data in self.gastos)


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.imoveis = {}
        self.initUI()
        self.imovel_selecionado = None 
        self.mostrando_imoveis = False
        self.itens_imoveis = []
        self.carregar_imoveis()
        self.btn_adicionar_gasto.hide()
        self.btn_ver_gastos.hide()
        
    def initUI(self):
        
        self.setWindowTitle('Controle de Gastos de Imóveis')
        self.resize( 1672, 690)

                # Criar a barra de menu
        self.menubar = QMenuBar(self)
        self.setMenuBar(self.menubar)
        

        # Criar o menu "Opções"
        self.menuOpcoes = QMenu("Opções", self)
        self.menubar.addMenu(self.menuOpcoes)

        # Criar a barra de ferramentas
        self.toolBar = QToolBar(self)
        self.addToolBar(Qt.TopToolBarArea, self.toolBar)

        # Criar ações
        self.action_procurar = QAction(QIcon(":/main(images)/buscar.png"), "Procurar", self)
        self.action_cadastrar = QAction(QIcon(":/main(images)/create.png"), "Cadastrar", self)
        self.action_apagar = QAction(QIcon(":/main(images)/delete.png"), "Apagar", self)
        self.action_atualizar = QAction(QIcon(":/main(images)/refresh.png"), "Atualizar", self)
        
         # Conectar a ação "Apagar" com o método de apagar imóvel
        self.action_apagar.triggered.connect(self.apagar_imovel)

        # Adicionar ações à barra de ferramentas e ao menu
        self.toolBar.addAction(self.action_procurar)
        self.toolBar.addAction(self.action_cadastrar)
        self.toolBar.addAction(self.action_apagar)
        self.toolBar.addAction(self.action_atualizar)

        self.menuOpcoes.addAction(self.action_procurar)
        self.menuOpcoes.addAction(self.action_cadastrar)
        self.menuOpcoes.addAction(self.action_apagar)
        self.menuOpcoes.addAction(self.action_atualizar)

        # Definir dicas de ferramentas para ações
        self.action_procurar.setToolTip("Procurar Imóvel")
        self.action_cadastrar.setToolTip("Cadastrar Imóvel")
        self.action_apagar.setToolTip("Apagar Imóvel")
        self.action_atualizar.setToolTip("Atualizar Tela")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.header = QLabel('CONTROLE DE GASTOS', self.central_widget)
        self.header.setAlignment(Qt.AlignCenter)
        self.header.setStyleSheet("font: 75 12pt \"HP Simplified\";\n"
"color: rgb(255, 255, 255);\n"
"\n"
"\n"
"background-color: qlineargradient(spread:reflect, x1:0.284, y1:0.948636, x2:1, y2:0.916, stop:0.4375 rgba(0, 0, 64, 255), stop:0.568182 rgba(0, 0, 93, 255), stop:0.670455 rgba(0, 0, 102, 255), stop:0.789773 rgba(0, 18, 117, 255), stop:0.954545 rgba(0, 57, 142, 255), stop:1 rgba(0, 81, 127, 255));\n"
"border-top-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(0, 0, 0, 255), stop:1 rgba(255, 255, 255, 255));\n"
"")
        self.header.setFixedHeight(50)
        self.header.setFont(QFont('Arial', 16))
        self.main_layout.addWidget(self.header)
        self.content_layout = QHBoxLayout()
        self.main_layout.addLayout(self.content_layout)
        
        self.navbar = QListWidget()
        
        self.navbar.setMaximumWidth(200)
        # Estilizar o NavBar
        self.navbar.setStyleSheet("""
            QListWidget {
                background-color: #f0f0f0;  # Cor de fundo mais suave
                border: none;  # Remover bordas
                padding: 10px;  # Espaçamento interno
                font-family: Arial;  # Tipo de fonte
            }
            QListWidget::item {
                border-bottom: 1px solid #e0e0e0;  # Linha separadora
            }
            QPushButton {
                background-color: #4CAF50;  # Cor do botão
                color: white;  # Cor do texto
                border-radius: 5px;  # Bordas arredondadas
                padding: 10px;  # Espaçamento interno
                margin: 5px;  # Espaçamento externo
            }
            QPushButton:hover {
                background-color: #45a049;  # Cor do botão ao passar o mouse
            }
        """)

        self.navbar.currentItemChanged.connect(self.imovel_selecionado)
        self.content_layout.addWidget(self.navbar)
        self.navbar_header = QListWidgetItem('IMÓVEIS')
        
        # Criar um gradiente linear
        gradient = QLinearGradient(0, 0, 0, 40)  # Gradiente vertical
        gradient.setColorAt(0.4375, QColor(0, 0, 64))
        gradient.setColorAt(0.568182, QColor(0, 0, 93))
        gradient.setColorAt(0.670455, QColor(0, 0, 102))
        gradient.setColorAt(0.789773, QColor(0, 18, 117))
        gradient.setColorAt(0.954545, QColor(0, 57, 142))
        gradient.setColorAt(1, QColor(0, 81, 127))

        # Definir o gradiente como fundo do QListWidgetItem
        self.navbar_header.setBackground(QBrush(gradient))
        self.navbar_header.setForeground(Qt.white)  # Define a cor do texto para branco
        
        self.navbar_header.setSizeHint(QSize(200, 40))
        self.navbar_header.setTextAlignment(Qt.AlignCenter) 
        self.navbar.addItem(self.navbar_header)
        self.adicionar_imovel_item = QListWidgetItem(self.navbar)
        self.navbar.addItem(self.adicionar_imovel_item)
        self.adicionar_imovel_btn = QPushButton('Adicionar Imóvel', self.navbar)
        self.adicionar_imovel_btn.setStyleSheet("background-color: lightblue; color: black;")
        self.adicionar_imovel_btn.clicked.connect(self.adicionar_imovel)
        self.navbar.setItemWidget(self.adicionar_imovel_item, self.adicionar_imovel_btn)
        self.meus_imoveis_item = QListWidgetItem(self.navbar)
        self.navbar.addItem(self.meus_imoveis_item)
        self.meus_imoveis_btn = QPushButton('Meus Imóveis', self.navbar)
        self.meus_imoveis_btn.setStyleSheet("background-color: lightblue; color: black;")
        self.meus_imoveis_btn.clicked.connect(self.mostrar_meus_imoveis)
        self.navbar.setItemWidget(self.meus_imoveis_item, self.meus_imoveis_btn)
        self.stack = QStackedWidget()
        self.content_layout.addWidget(self.stack)
        self.tela_inicial = QWidget()
        self.label_tela_inicial = QLabel("Selecione um imóvel para ver ou adicionar gastos.", self.tela_inicial)
        self.label_tela_inicial.setAlignment(Qt.AlignCenter)
        self.stack.addWidget(self.tela_inicial)
        self.tela_opcoes_imovel = QWidget()
        self.opcoes_imovel_layout = QVBoxLayout(self.tela_opcoes_imovel)
        self.stack.addWidget(self.tela_opcoes_imovel)
        self.btn_adicionar_gasto = QPushButton('Adicionar Gasto', self.tela_opcoes_imovel)

        self.opcoes_imovel_layout.setAlignment(QtCore.Qt.AlignTop)
        
        self.btn_adicionar_gasto.setFixedWidth(211)
        self.btn_adicionar_gasto.setFixedHeight(61)
        self.btn_adicionar_gasto.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_adicionar_gasto.setStyleSheet("background-color: qlineargradient(spread:reflect, x1:0.284, y1:0.948636, x2:1, y2:0.916, stop:0.4375 rgba(0, 0, 64, 255), stop:0.568182 rgba(0, 0, 93, 255), stop:0.670455 rgba(0, 0, 102, 255), stop:0.789773 rgba(0, 18, 117, 255), stop:0.954545 rgba(0, 57, 142, 255), stop:1 rgba(0, 81, 127, 255));\n"
"border-top-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(0, 0, 0, 255), stop:1 rgba(255, 255, 255, 255));\n"
"\n"
"gridline-color: rgb(255, 255, 255);\n"
"color: rgb(255, 255, 255);\n"
"color: rgb(255, 255, 255);\n"
"\n"
 "border-radius: 5px;"
"font: 75 10pt \"Segoe UI Variable Small\";\n"
"")
        self.btn_adicionar_gasto.clicked.connect(self.mostrar_adicionar_gasto)
        self.opcoes_imovel_layout.addWidget(self.btn_adicionar_gasto)
        self.btn_ver_gastos = QPushButton('Ver Gastos', self.tela_opcoes_imovel)
        self.btn_ver_gastos.setGeometry(QtCore.QRect(50, 120, 211, 61))   # Set new coordinates (x, y) for Ver Gastos button
        self.btn_ver_gastos.setFixedWidth(211)
        self.btn_ver_gastos.setFixedHeight(61)
        self.btn_ver_gastos.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_ver_gastos.setStyleSheet("background-color: qlineargradient(spread:reflect, x1:0.284, y1:0.948636, x2:1, y2:0.916, stop:0.4375 rgba(0, 0, 64, 255), stop:0.568182 rgba(0, 0, 93, 255), stop:0.670455 rgba(0, 0, 102, 255), stop:0.789773 rgba(0, 18, 117, 255), stop:0.954545 rgba(0, 57, 142, 255), stop:1 rgba(0, 81, 127, 255));\n"
"border-top-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(0, 0, 0, 255), stop:1 rgba(255, 255, 255, 255));\n"
"\n"
"gridline-color: rgb(255, 255, 255);\n"
"color: rgb(255, 255, 255);\n"
"color: rgb(255, 255, 255);\n"
"border-radius: 5px;"
"\n"
"font: 75 10pt \"Segoe UI Variable Small\";\n"
"")
        self.btn_ver_gastos.clicked.connect(self.mostrar_ver_gastos)
        self.botao_voltar = self.criar_botao_voltar()
        self.botao_voltar.hide()
        self.opcoes_imovel_layout.addWidget(self.btn_ver_gastos)
        
        
# Inicialização do widget para Adicionar Gastos
        self.adicionar_gasto_widget = QWidget()
        self.adicionar_gasto_layout = QVBoxLayout(self.adicionar_gasto_widget)
        self.adicionar_gasto_layout.setSpacing(0)  # Reduzir o espaçamento entre sublayouts
        self.adicionar_gasto_layout.setContentsMargins(50, 20, 0, 150)  # Reduzir as margens do layout
        self.adicionar_gasto_widget.setMaximumWidth(400)


        # Item Input
        self.item_input = QLineEdit(self.adicionar_gasto_widget)
        self.item_input.setPlaceholderText("Item")
        self.adicionar_gasto_layout.addWidget(self.item_input)

        # Forma de Pagamento
        self.forma_pagamento_input = QComboBox(self.adicionar_gasto_widget)
        self.forma_pagamento_input.addItems(["Cartão", "Dinheiro", "Pix", "Boleto", "Cheque"])
        self.adicionar_gasto_layout.addWidget(self.forma_pagamento_input)

        # Valor Input
        self.valor_input = QLineEdit(self.adicionar_gasto_widget)
        self.valor_input.setPlaceholderText("Valor")
        self.adicionar_gasto_layout.addWidget(self.valor_input)

        # Data Input
        self.data_input = QLineEdit(self.adicionar_gasto_widget)
        self.data_input.setPlaceholderText("Data (YYYY-MM-DD)")
        self.data_input.mousePressEvent = self.mostrar_calendario  # Intercepta o evento de clique
        self.data_input.hide()  # # Ocultar o campo de entrada de data inicialmente
        self.data_input.mousePressEvent = self.mostrar_calendario
        self.adicionar_gasto_layout.addWidget(self.data_input)



    
        # Inicialização do widget para Ver Gastos
        self.mostrar_gastos_widget = QWidget()
        self.mostrar_gastos_layout = QVBoxLayout(self.mostrar_gastos_widget)

        # Adicionar QLabel na tela de Ver Gastos
        self.nome_imovel_label_ver = QLabel("Selecione um imóvel", self.mostrar_gastos_widget)
        self.nome_imovel_label_ver.setFont(QFont('Arial', 12))
        self.mostrar_gastos_layout.addWidget(self.nome_imovel_label_ver, 0, Qt.AlignTop)
        
        self.stack.addWidget(self.adicionar_gasto_widget)
        


        
        self.adicionar_gasto_widget.setStyleSheet("""
            QLineEdit {
                border: 1px solid #BDBDBD;
                border-radius: 5px;
                padding: 20px;
                height:10px;
    

                
            }
            

            
            
            QComboBox{
                border: 1px solid #BDBDBD;
                border-radius: 5px;
                padding: 20px;
                height:10px;
    

                
            }
            QPushButton {
                background-color: #4CAF50;
                border: none;
                border-radius: 5px;
                color: white;
                padding: 20px 15px;
                text-align: center;
                text-decoration: none;
        
                font-size: 16px;
                margin: 4px 2px;
         
            }

        """)
        

        
        # Primeiro, crie um widget para o card e defina o seu layout
        self.card_widget = QWidget(self.adicionar_gasto_widget)
        self.card_layout = QVBoxLayout(self.card_widget)

        # Ajuste do layout de adicionar gastos
        self.adicionar_gasto_layout.setSpacing(2)  # Define o espaçamento entre os widgets

        # Adicionando a legenda para o campo "Item" e o próprio campo
        item_label = QLabel("Item:", self.adicionar_gasto_widget)
        self.adicionar_gasto_layout.addWidget(item_label)
        self.adicionar_gasto_layout.addWidget(self.item_input)
        self.adicionar_gasto_layout.addStretch(1)  # Adiciona um espaço expansível
 

        # Adicionando a legenda para o campo "Forma de Pagamento"
        forma_pagamento_label = QLabel("Forma de Pagamento:", self.adicionar_gasto_widget)
        self.adicionar_gasto_layout.addWidget(forma_pagamento_label)
        self.adicionar_gasto_layout.addWidget(self.forma_pagamento_input)
        self.adicionar_gasto_layout.addStretch(1)  # Adiciona um espaço expansível
        # Adicionando a legenda para o campo "Valor"
        valor_label = QLabel("Valor:", self.adicionar_gasto_widget)
        self.adicionar_gasto_layout.addWidget(valor_label)
        self.adicionar_gasto_layout.addWidget(self.valor_input)
        self.adicionar_gasto_layout.addStretch(1)  # Adiciona um espaço expansível
        # Adicionando a legenda para o campo "Data"
        data_label = QLabel("Data:", self.adicionar_gasto_widget)
        self.adicionar_gasto_layout.addWidget(data_label)
        self.adicionar_gasto_layout.addWidget(self.data_input)
        self.adicionar_gasto_layout.addStretch(1)  # Adiciona um espaço expansível

        self.confirmar_gasto_btn = QPushButton('Confirmar Gasto', self.adicionar_gasto_widget)
        self.confirmar_gasto_btn.clicked.connect(self.confirmar_gasto)
        self.adicionar_gasto_layout.addWidget(self.confirmar_gasto_btn)
        self.mostrar_gastos_widget = QWidget()
        self.mostrar_gastos_layout = QVBoxLayout(self.mostrar_gastos_widget)
        self.stack.addWidget(self.mostrar_gastos_widget)
        self.tabela_gastos = QTableWidget(0, 4, self.mostrar_gastos_widget)
        self.tabela_gastos.setHorizontalHeaderLabels(["Item", "Forma de pagamento", "Valor","Data"])
        self.tabela_gastos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.mostrar_gastos_layout.addWidget(self.tabela_gastos)
        self.total_label = QLabel("Total: R$0.00", self.mostrar_gastos_widget)
        self.mostrar_gastos_layout.addWidget(self.total_label)
        
        self.show()
        
        


    def apagar_imovel(self):
            if self.tabela_gastos.currentRow() >= 0:
                self.apagar_item_gasto()
   
                
            elif self.imovel_selecionado:
                self.apagar_imovel_selecionado()
                self.carregar_imoveis()
            else:
                QMessageBox.warning(self, "Atenção", "É necessário selecionar um Imóvel ou um Item de Gasto primeiro para deletar.")
  

    def apagar_item_gasto(self):
        # Implementação para apagar o item de gasto selecionado
        row = self.tabela_gastos.currentRow()
        item_id = self.tabela_gastos.item(row, 0).data(Qt.UserRole)  # Supondo que o ID está armazenado como UserRole
        resposta = QMessageBox.question(self, "Confirmar Exclusão", "Tem certeza que deseja apagar este item de gasto?", QMessageBox.Yes | QMessageBox.No)
        
        if resposta == QMessageBox.Yes:
            # Aqui você deverá implementar a lógica para apagar o item do banco de dados
            conn = conectar_mysql()
            if conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM itens WHERE id = %s', (item_id,))
                conn.commit()
                conn.close()
            self.atualizar_tabela_gastos(self.imovel_selecionado.nome)

    def apagar_imovel_selecionado(self):
            nome_imovel = self.imovel_selecionado.nome
            resposta = QMessageBox.question(self, "Confirmar Exclusão", f"Tem certeza que deseja apagar o imóvel '{nome_imovel}'?", QMessageBox.Yes | QMessageBox.No)
            
            if resposta == QMessageBox.Yes:
                self.excluir_imovel(nome_imovel)
                QMessageBox.information(self, 'Exclusão', f'Imóvel "{nome_imovel}" excluído com sucesso.')
                self.carregar_imoveis()

    def excluir_imovel(self, nome_imovel):
        conn = conectar_mysql()
        if conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM imoveis WHERE nome = %s', (nome_imovel,))
            conn.commit()
            conn.close()

        # Remover o imóvel da lista de imóveis do programa
        if nome_imovel in self.imoveis:
            del self.imoveis[nome_imovel]
            
     
            
            
    def adicionar_imovel(self):
        nome, ok = QInputDialog.getText(self, 'Adicionar Imóvel', 'Nome do Imóvel:')
        if ok and nome:
            novo_imovel = Imovel(nome)
            self.imoveis[nome] = novo_imovel
            self.navbar.addItem(nome)

            # Inserir o nome do imóvel no banco de dados
            conn = conectar_mysql()
            if conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO imoveis (nome) VALUES (%s)', (nome,))
                conn.commit()
                conn.close()
                
    def carregar_imoveis(self):
        

        conn = conectar_mysql()
        if conn:
            cursor = conn.cursor()
            cursor.execute('SELECT nome FROM imoveis')
            for row in cursor.fetchall():
                nome_imovel = row[0]
                if nome_imovel not in self.imoveis:  # Verifica se já está na lista
                    self.imoveis[nome_imovel] = Imovel(nome_imovel)  # Adiciona ao dicionário
            conn.close()
            
        
            
        
    def mostrar_calendario(self, event):
        self.calendario = QCalendarWidget(self)
        self.calendario.setWindowModality(Qt.ApplicationModal)
        self.calendario.clicked.connect(self.selecionar_data)
        self.calendario.setWindowTitle('Escolher Data')
        self.calendario.setGeometry(100, 100, 300, 200)
        self.calendario.show()
        
    def mostrar_meus_imoveis(self):
        if self.mostrando_imoveis:
            # Remove os itens de imóveis da navbar
            for nome_imovel in self.imoveis:
                for index in range(self.navbar.count()):
                    item = self.navbar.item(index)
                    if item and item.text() == nome_imovel:
                        self.navbar.takeItem(index)
                        break
            self.mostrando_imoveis = False
        else:
            # Adiciona os itens de imóveis na navbar
            for nome_imovel in self.imoveis:
                item_encontrado = False
                for index in range(self.navbar.count()):
                    item = self.navbar.item(index)
                    if item and item.text() == nome_imovel:
                        item_encontrado = True
                        break
                if not item_encontrado:
                    self.navbar.addItem(nome_imovel)
            self.mostrando_imoveis = True

    def selecionar_data(self, date):
        selected_date = date.toString("yyyy-MM-dd")
        self.data_input.setText(selected_date)
        self.calendario.close()

    def imovel_selecionado(self, current, previous):
        if current and current.text() in self.imoveis:
            nome_imovel = current.text()
            self.imovel_selecionado = self.imoveis[nome_imovel]

            # Atualizar o texto do cabeçalho para o nome do imóvel
            self.header.setText(f"{nome_imovel}")
            self.stack.setCurrentWidget(self.tela_opcoes_imovel)
            self.btn_adicionar_gasto.show()
            self.btn_ver_gastos.show()
        else:
            self.imovel_selecionado = None
            self.stack.setCurrentWidget(self.tela_inicial)
            self.btn_adicionar_gasto.hide()
            self.btn_ver_gastos.hide()
            # Restaurar o texto original do cabeçalho
            self.header.setText("CONTROLE DE GASTOS")

    def mostrar_adicionar_gasto(self):
        if self.imovel_selecionado:
            # Atualizar o texto do cabeçalho para o nome do imóvel
            self.header.setText(f"Adicionar despesa em {self.imovel_selecionado.nome}")
            self.stack.setCurrentWidget(self.adicionar_gasto_widget)
            self.botao_voltar.show()
            self.data_input.show() # Mostrar campo de entrada de data
        else:
            self.exibir_mensagem("Por favor, selecione um imóvel primeiro.")


    def mostrar_ver_gastos(self):
        if self.imovel_selecionado:
            # Atualizar o texto do cabeçalho para o nome do imóvel
            self.header.setText(f"Gastos do Imóvel {self.imovel_selecionado.nome}")
            self.atualizar_tabela_gastos(self.imovel_selecionado.nome)
            self.stack.setCurrentWidget(self.mostrar_gastos_widget)
            self.botao_voltar.show()
        else:
            print("Por favor, selecione um imóvel primeiro.")


    def criar_botao_voltar(self):
        botao_voltar = QPushButton('Voltar', self)
        botao_voltar.clicked.connect(self.voltar_para_selecao_imovel)
        return botao_voltar

    def voltar_para_selecao_imovel(self):
        # Restaurar o texto original do cabeçalho
        self.header.setText("CONTROLE DE GASTOS")

        self.stack.setCurrentWidget(self.tela_opcoes_imovel)
        self.navbar.setCurrentItem(self.navbar_header)  # Selecionar o cabeçalho da lista
        self.botao_voltar.hide()  # Ocultar o botão "Voltar" ao retornar

    
    def confirmar_gasto(self):
        nome_imovel = self.navbar.currentItem().text()
        if nome_imovel in self.imoveis:
            item = self.item_input.text()
            forma_pagamento = self.forma_pagamento_input.currentText()
            valor_texto = self.valor_input.text().replace(',', '.')
            data = self.data_input.text()

            # Verificar se todos os campos foram preenchidos
            if not item or not forma_pagamento or not valor_texto or not data:
                QMessageBox.warning(self, 'Atenção', 'Por favor, preencha todos os campos.')
                return

            try:
                valor_float = float(valor_texto)
                self.imoveis[nome_imovel].adicionar_gasto(item, forma_pagamento, valor_float, data)
                self.item_input.clear()
                self.forma_pagamento_input.setCurrentIndex(0)
                self.valor_input.clear()
                self.data_input.clear()
                self.atualizar_tabela_gastos(nome_imovel)

                # Exibir modal de confirmação
                QMessageBox.information(self, 'Sucesso', 'Despesa registrada com sucesso.')

                # Mudar a tela atual para a tela de opções do imóvel
                self.stack.setCurrentWidget(self.tela_opcoes_imovel)

            except ValueError:
                QMessageBox.warning(self, 'Erro', 'Por favor, insira um valor numérico válido.')
        else:
            QMessageBox.warning(self, 'Atenção', 'Por favor, selecione um imóvel primeiro.')


    def atualizar_tabela_gastos(self, nome_imovel):
        # Obter o ID do imóvel selecionado
        id_imovel = self.imoveis[nome_imovel].obter_id_imovel(nome_imovel)

        # Conectar ao banco de dados e buscar os gastos para esse imóvel
        conn = conectar_mysql()
        if conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, item, forma_pg, valor, data FROM itens WHERE id_imovel = %s', (id_imovel,))
            self.tabela_gastos.setRowCount(0)
            total = 0
            for id_item, item, forma_pagamento, valor, data in cursor.fetchall():
                row_position = self.tabela_gastos.rowCount()
                self.tabela_gastos.insertRow(row_position)
                item_widget = QTableWidgetItem(item)
                item_widget.setData(Qt.UserRole, id_item)  # Armazenar o ID do item
                self.tabela_gastos.setItem(row_position, 0, item_widget)
                self.tabela_gastos.setItem(row_position, 1, QTableWidgetItem(forma_pagamento))
                self.tabela_gastos.setItem(row_position, 2, QTableWidgetItem(f'R${valor:.2f}'))
                self.tabela_gastos.setItem(row_position, 3, QTableWidgetItem(str(data)))
                total += valor
            self.total_label.setText(f"Total: R${total:.2f}")
            conn.close()


    
def main():
    conn = conectar_mysql()
    if conn:
        criar_tabelas_mysql(conn)
        conn.close()
    app = QApplication(sys.argv)
    ex = MainApp()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
