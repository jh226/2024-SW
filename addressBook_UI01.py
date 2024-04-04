import sys
from PyQt5.QtWidgets import QInputDialog, QApplication, QMainWindow, QFileDialog, QListWidgetItem, QMessageBox
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap, QIcon

# 오른쪽 버튼 눌러서 삭제 메뉴 만들기 위해
from PyQt5.QtWidgets import QMenu, QAction
from PyQt5.QtCore import Qt, QEvent

#DB 연결
from addBookMySQL import *

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # UI 파일을 로드합니다.
        loadUi('D:/dev/myPrj03/res/ui01.ui', self)
        self.setWindowTitle('주소록 Ver1')
        
        #DB 객체 생성
        self.db = mysqlDB()
        print(self.db)

        # 이미지 파일의 경로를 저장하는 변수를 초기화합니다.
        self.image_paths = []

        # 빈 이미지를 생성합니다.
        self.empty_pixmap = QPixmap()
        self.default_pixmap = QPixmap('./res/unknown.png')  # 디폴트 이미지 경로

        # 실행시 주소록 읽어 오기
        self.load_address_book()

        # pushButton이 클릭되었을 때의 동작을 연결합니다.
        self.pushButton.clicked.connect(self.open_image_dialog)
        # pushButton_2이 클릭되었을 때의 동작을 연결합니다.
        self.pushButton_2.clicked.connect(self.Reload_address_book)
        # pushButton_3이 클릭되었을 때의 동작을 연결합니다.
        self.pushButton_3.clicked.connect(self.save_address_book)
        # lineEdit에 대한 returnPressed 시그널을 연결합니다.
        self.lineEdit.returnPressed.connect(self.add_to_address_book)
        # pushButton_4이 클릭되었을 때의 동작을 연결합니다.
        self.pushButton_4.clicked.connect(self.add_to_address_book)
        # listWidget에 컨텍스트 메뉴 삭제 를 추가합니다.
        self.listWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listWidget.customContextMenuRequested.connect(self.show_context_menu)
         # 리스트 위젯 아이템 클릭 시 정보를 표시하기 위한 시그널 연결
        self.listWidget.itemClicked.connect(self.display_info)
        
        # 입력칸을 클릭했을 때 기존 내용을 지우는 이벤트 처리
        self.lineEdit.installEventFilter(self)
        self.lineEdit_2.installEventFilter(self)
        
        # 저장 여부 확인을 위한 변수
        self.unsaved_changes = False

    def eventFilter(self, obj, event):
        if obj == self.lineEdit and event.type() == QEvent.FocusIn:
            self.lineEdit.clear()
            self.lineEdit_2.clear()
            self.label_3.clear()
            self.label_4.setText("선택된 이미지 없음")
        return super().eventFilter(obj, event)
    
    def show_context_menu(self, pos):
        # 컨텍스트 메뉴를 생성합니다.
        context_menu = QMenu()
        delete_action = QAction(QIcon('./res/delete_icon.png'),"삭제", self)
        delete_action.triggered.connect(self.delete_item)
        context_menu.addAction(delete_action)
        
        update_action = QAction(QIcon('./res/edit_icon.png'),"수정", self)
        update_action.triggered.connect(self.update_item)
        context_menu.addAction(update_action)

        # 컨텍스트 메뉴를 보여줍니다.
        context_menu.exec_(self.listWidget.mapToGlobal(pos))

    def delete_item(self):
        # 선택된 아이템을 삭제합니다.
        selected_items = self.listWidget.selectedItems()
        for item in selected_items:
            row = self.listWidget.row(item)
            self.listWidget.takeItem(row)
            
            name, phone = item.text().split(' - ')
            self.db.delete(name, phone)
            
    def update_item(self):
        selected_items = self.listWidget.selectedItems()
    
        # 선택된 아이템이 없으면 함수를 종료합니다.
        if not selected_items:
            return

        # 첫 번째 선택된 아이템을 가져옵니다.
        selected_item = selected_items[0]

        # 아이템의 텍스트에서 이름과 전화번호를 가져옵니다.
        old_text = selected_item.text()
        old_name, old_phone = old_text.split(' - ')
        
        # 수정 다이얼로그를 열어서 사용자로부터 새로운 정보를 입력받습니다.
        new_name, ok1 = QInputDialog.getText(self, '연락처 수정', '이름:', text=old_name)
        new_phone, ok2 = QInputDialog.getText(self, '연락처 수정', '전화번호:', text=old_phone)
        
        # 사용자가 확인을 누르지 않았거나 빈 입력값이라면 함수를 종료합니다.
        if not (ok1 and ok2) or not (new_name.strip() and new_phone.strip()):
            return
        
        filename = ""
        
         # 사진 수정 여부를 묻는 메시지를 표시합니다.
        reply = QMessageBox.question(self, '사진 수정', '사진을 수정하시겠습니까?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        # 사용자가 "예"를 선택한 경우에만 사진 수정 다이얼로그를 엽니다.
        if reply == QMessageBox.Yes:
            # 이미지 파일 선택 다이얼로그를 엽니다.
            filename, _ = QFileDialog.getOpenFileName(self, '새 이미지 파일 선택', '', '이미지 파일 (*.png *.jpg *.jpeg *.bmp *.gif)')
            if filename:
                # 선택한 이미지 파일을 불러옵니다.
                pixmap = QPixmap(filename)
                # 이미지를 새로운 이미지로 업데이트합니다.
                selected_item.setIcon(QIcon(pixmap))
                new_photo_path = filename
                
        elif reply == QMessageBox.No:
            index = self.listWidget.row(selected_item)
            new_photo_path = self.image_paths[index]
        
        #DB 수정
        self.db.update(old_name, new_phone, filename)
                
        

        # 새로운 아이템 텍스트를 구성합니다.
        new_text = f"{new_name.strip()} - {new_phone.strip()}"
        
        # 아이템의 텍스트를 업데이트합니다.
        selected_item.setText(new_text)

        # 수정된 연락처 정보를 저장합니다.
        index = self.listWidget.row(selected_item)
        self.image_paths[index] = new_photo_path if new_photo_path else self.image_paths[index]

        # 수정된 연락처 정보를 저장했다는 메시지를 표시합니다.
        QMessageBox.information(self, '연락처 수정', '연락처가 성공적으로 수정되었습니다.')

    def display_info(self, item):
        # 클릭된 아이템에서 이름과 전화번호를 가져옵니다.
        name, phone = item.text().split(' - ')
        
        # 해당 정보를 표시합니다.
        self.lineEdit.setText(name)
        self.lineEdit_2.setText(phone)

        # 해당 아이템의 이미지 파일 경로를 가져옵니다.
        photo_path = self.image_paths[self.listWidget.row(item)]

        # 선택한 이미지 파일을 불러와서 라벨에 표시합니다.
        if photo_path.strip().lower() != 'none':
            pixmap = QPixmap(photo_path)
        else:
            pixmap = self.empty_pixmap

        self.label_3.setPixmap(pixmap)
        self.label_3.setScaledContents(True)

    def load_address_book(self):
        # DB에서 주소록 데이터를 가져옵니다.
        address_book_data = self.db.select_all()

        # 가져온 데이터를 순회하면서 QListWidget에 추가합니다.
        for data in address_book_data:
            name = data['name']
            phone = data['phone']
            filename = data['filename']

            # QListWidgetItem을 생성합니다.
            item = QListWidgetItem(f"{name} - {phone}")

            # 이미지 파일의 경로를 저장합니다.
            self.image_paths.append(filename)

            # 사진이 있는 경우에는 사진을 표시하고, 없는 경우에는 빈 이미지를 표시합니다.
            if filename.strip():
                pixmap = QPixmap(filename)
            else:
                pixmap = self.default_pixmap

            # QListWidgetItem에 아이콘을 설정합니다.
            icon = QIcon(pixmap)
            item.setIcon(icon)

            # QListWidget에 item을 추가합니다.
            self.listWidget.addItem(item)
                   
    def save_address_book(self):
        print('')
        # 파일 다이얼로그를 엽니다.
        # filename = 'addbook2.txt'

        # # 만약 사용자가 파일을 선택했다면
        # if filename:
        #     # listWidget의 아이템을 파일에 저장합니다.
        #     with open(filename, 'w') as file:
        #         for index in range(self.listWidget.count()):
        #             item = self.listWidget.item(index)
        #             # 아이템에서 이름과 전화번호를 가져옵니다.
        #             name, phone = item.text().split(' - ')                    
        #             # 아이콘의 파일 경로를 가져옵니다.                    
        #             photo_path = self.image_paths[index]  # 해당 아이템의 이미지 파일 경로를 가져옵니다.
        #             # 이름, 전화번호, 이미지 파일 경로를 파일에 씁니다.
        #             file.write(name + ',' + phone + ',' + photo_path + '\n')
        #     # 주소록을 저장했다는 메시지를 표시합니다.
        #     QMessageBox.information(self, '주소록 저장', '주소록이 성공적으로 저장되었습니다.')

    def add_to_address_book(self):
        # lineEdit에 입력된 텍스트를 가져옵니다.
        name = self.lineEdit.text().strip()
        phone = self.lineEdit_2.text().strip()
        photo_path = self.label_4.text().strip()

        # 가져온 데이터가 비어있지 않은 경우에만 주소록에 추가합니다.
        if name and phone:
            # QListWidgetItem을 생성합니다.
            item = QListWidgetItem(name + ' - ' + phone)
            
            # 사진이 있는 경우에는 해당 사진을 표시하고, 없는 경우에는 빈 이미지를 표시합니다.
            if photo_path.strip().lower() != 'none':
                pixmap = QPixmap(photo_path)
            else:
                pixmap = self.empty_pixmap

            # QListWidgetItem에 아이콘을 설정합니다.
            item.setIcon(QIcon(pixmap))

            # QListWidget에 item을 추가합니다.
            self.listWidget.addItem(item)
            
            # 이미지 파일의 경로를 저장합니다.
            self.image_paths.append(photo_path)
            
            result = self.db.insert(name, phone, photo_path)

            # lineEdit을 초기화합니다.
            self.lineEdit.clear()
            self.lineEdit_2.clear()
            self.label_3.clear()
            self.label_4.setText("선택된 이미지 없음")

    def open_image_dialog(self):
        # 파일 다이얼로그를 엽니다.
        filename, _ = QFileDialog.getOpenFileName(self, '이미지 파일 선택', '', '이미지 파일 (*.png *.jpg *.jpeg *.bmp *.gif)')

        # 만약 사용자가 파일을 선택했다면
        if filename:
             # 선택한 이미지 파일을 불러옵니다.
            pixmap = QPixmap(filename)
                    
            self.label_3.setPixmap(pixmap)
            self.label_3.setScaledContents(True)
            self.label_4.setText(filename)

    def Reload_address_book(self):
         if self.lineEdit.text() or self.lineEdit_2.text() or self.label_3.pixmap() or self.label_4.text():
                reply = QMessageBox.question(self, '저장 확인', '저장되지 않은 변경 사항이 있습니다. 저장하시겠습니까?',
                                         QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Cancel)
                if reply == QMessageBox.Yes:
                    self.save_address_book()
                    self.reload()
                elif reply == QMessageBox.No:
                    self.reload()
                else:
                    pass
         else:
            self.reload()
    
    def reload(self):
        # 주소록을 초기화합니다.
        self.listWidget.clear()
        self.image_paths.clear()

        # 주소록을 다시 불러옵니다.
        self.load_address_book()
        
        # 입력 칸과 이미지 라벨을 초기화합니다.
        self.lineEdit.clear()
        self.lineEdit_2.clear()
        self.label_3.clear()
        self.label_4.setText("선택된 이미지 없음")
           
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
