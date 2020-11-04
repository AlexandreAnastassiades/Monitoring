# pylint: disable-all
""" Monitoring project methods , getting data from aws server  """
from __future__ import print_function
import paramiko
from paramiko.ssh_exception import BadHostKeyException, AuthenticationException, SSHException
import socket



SERVER_ONE = "52.4.91.83"
SERVER_TWO = "34.237.227.179"
SERVERS = [SERVER_ONE, SERVER_TWO]
LOGIN_SERVER_ONE = "interfadm"
PASS_SERVER_ONE = "Projet654!"


def connect_to_server_ssh(adress, user, pdw):
    ''' Connect to Server SSH return the client  '''
    client = paramiko.client.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.load_system_host_keys()
    client.connect(adress, username=user, password=pdw)
    return client


def get_access_log_data_error_pages(adress, user, pdw):
    ''' Return values : First value -> number of error pages
                    Second value -> number of working pages
                    Third value -> number of total pages '''
    client = connect_to_server_ssh(adress, user, pdw)
    stdin, stdout_404_error, stderr = client.exec_command(
        "cd /var/log ; cd apache2; grep 404 access.log | wc -l  ")
    stdin, stdout_number_line, stderr = client.exec_command(
        "cd /var/log ; cd apache2; cat access.log | wc -l  ")
    stdin, stdout_working, stderr = client.exec_command(
        "cd /var/log ; cd apache2; grep 200 access.log | wc -l  ")

    print(stdin, stderr)
    line_404_error = stdout_404_error.readlines()
    line_number_line = stdout_number_line.readlines()
    line_working = stdout_working.readlines()

    errors = int(''.join(line_404_error))
    number_of_line = int(''.join(line_number_line))
    working = int(''.join(line_working))

    return errors, working, number_of_line


def get_error_log_data(adress, user, pdw):
    ''' Write the error.log file into a local file '''
    client = connect_to_server_ssh(adress, user, pdw)
    stdin, stdout_meminf, stderr = client.exec_command(
        "cd /var/log ; cd apache2; cat error.log ")
    line_meminfo = stdout_meminf.readlines()
    resp = ''.join(line_meminfo)
    print(stdin, stderr)
    print("getting data from error.log")
    log_file = open("error.csv", "a")
    log_file.write(resp)
    log_file.close()


def get_other_log_data(adress, user, pdw):
    ''' Write other data on a local file  '''
    client = connect_to_server_ssh(adress, user, pdw)
    stdin, stdout_meminf, stderr = client.exec_command(
        "cd /var/log ; cd apache2; cat other_vhosts_access.log ")
    line_meminfo = stdout_meminf.readlines()
    print(stdin, stderr)
    resp = ''.join(line_meminfo)
    log_file = open("other_vhosts_access.log", "a")
    log_file.write(resp)
    log_file.close()


def get_ram_data(adress, user, pdw):
    """ Return memory Information total , free and available """

    client = connect_to_server_ssh(adress, user, pdw)
    stdin, stdout_mem_total, stderr = client.exec_command(
        'cat /proc/meminfo | grep MemTotal | cut -f2 -d: ')
    stdin, stdout_mem_free, stderr = client.exec_command(
        'cat /proc/meminfo | grep MemFree | cut -f2 -d: ')
    stdin, stdout_mem_available, stderr = client.exec_command(
        'cat /proc/meminfo | grep MemAvailable | cut -f2 -d: ')
    line_mem_total = stdout_mem_total.readlines()
    line_mem_free = stdout_mem_free.readlines()
    line_mem_available = stdout_mem_available.readlines()
    print(stdin, stderr)
    mem_total = int(''.join(line_mem_total).split(" ")[8])
    mem_free = int(''.join(line_mem_free).split(" ")[10])
    mem_available = int(''.join(line_mem_available).split(" ")[5])
    return mem_total, mem_free, mem_available


def get_processor_used(adress, user, pdw):
    client = connect_to_server_ssh(adress, user, pdw)
    stdin, stdout_top, stderr = client.exec_command("top -n1 -b | awk "+"'"+"BEGIN {line=0;}{line++;if(line==3){print $8}}"+"'")
    line_top = stdout_top.readlines()
    top = ''.join(line_top)
    top=top.replace("\n","")
    return float(top)

def get_cpu_name(adress, user, pdw):
    """ Return cpu name """
    client = connect_to_server_ssh(adress, user, pdw)
    stdin, stdout_cpu_name, stderr = client.exec_command(
        'cat /proc/cpuinfo | grep "model name" | cut -f2 -d: ')
    line_cpu_name = stdout_cpu_name.readline()
    cpu_name = ''.join(line_cpu_name)
    stdin, stdout_cpu_cores, stderr = client.exec_command(
        'cat /proc/cpuinfo | grep "cpu cores" | cut -f2 -d: ')
    line_cpu_cores = stdout_cpu_cores.readline()
    cpu_cores = ''.join(line_cpu_cores)
    stdin, stdout_cpu_cache, stderr = client.exec_command(
        'cat /proc/cpuinfo | grep "cache size" | cut -f2 -d: ')
    line_cpu_cache = stdout_cpu_cache.readline()
    cpu_cache = ''.join(line_cpu_cache)
    #print(stdin, stderr)
    return cpu_name, cpu_cores, cpu_cache


def get_ps(adress, user, pdw):
    """ Return data from ps command """
    client = connect_to_server_ssh(adress, user, pdw)
    stdin, stdout_number_process, stderr = client.exec_command('ps | wc -l')
    line_number_process = stdout_number_process.readlines()
    number_process = int(''.join(line_number_process)) - 1
    print(stdin, stderr)
    return number_process


def get_ip_config_data(adress, user, pdw):
    """ Return data about ifconfig command """
    client = connect_to_server_ssh(adress, user, pdw)
    if_config = {}
    stdin, stdout_if_config_tx, stderr = client.exec_command(
        "ifconfig | grep TX | grep bytes ")
    stdin, stdout_if_config_rx, stderr = client.exec_command(
        "ifconfig | grep RX | grep bytes ")
    line_stdout_if_config_tx = stdout_if_config_tx.readlines()
    line_stdout_if_config_rx = stdout_if_config_rx.readlines()

    if_config_rx_packet = int(''.join(line_stdout_if_config_rx).split(" ")[10])
    if_config_rx_bytes = int(''.join(line_stdout_if_config_rx).split(" ")[13])

    if_config_tx_packet = int(''.join(line_stdout_if_config_tx).split(" ")[10])
    if_config_tx_bytes = int(''.join(line_stdout_if_config_tx).split(" ")[13])

    if_config[adress] = {
        "tx_packet": if_config_tx_packet,
        "rx_packet": if_config_rx_packet,
        "rx_bytes": if_config_rx_bytes,
        "tx_bytes": if_config_tx_bytes
    }

    print(stdin, stderr)

    return if_config


def stdout_pages_data(adress, user, pdw):
    """ Return pages  """
    client = connect_to_server_ssh(adress, user, pdw)
    stdin, stdout_page_two, stderr = client.exec_command(
        "cd /var/log ; cd apache2; grep page2 access.log | wc -l  ")
    stdin, stdout_page_three, stderr = client.exec_command(
        "cd /var/log ; cd apache2; grep page3 access.log | wc -l  ")
    stdin, stdout_index, stderr = client.exec_command(
        "cd /var/log ; cd apache2; grep index access.log | wc -l  ")
    stdin, stdout_page_one, stderr = client.exec_command(
        "cd /var/log ; cd apache2; grep page1 access.log | wc -l  ")
    return stdout_page_one, stdout_page_two, stdout_page_three, stdout_index


def get_http_connections(adress, user, pdw):
    """ Number of http connections """
    visited_page = {}
    line_stdout_page_two = stdout_pages_data(adress, user, pdw)[1].readlines()
    line_stdout_index = stdout_pages_data(adress, user, pdw)[3].readlines()
    line_stdout_page_three = stdout_pages_data(adress, user, pdw)[
        2].readlines()
    line_stdout_page_one = stdout_pages_data(adress, user, pdw)[0].readlines()

    http_connections_page_one = int(
        ''.join(line_stdout_page_one))
    http_connections_page_two = int(
        ''.join(line_stdout_page_two))
    http_connections_page_three = int(
        ''.join(line_stdout_page_three))
    http_connections_index = int(''.join(line_stdout_index))
    visited_page = {
        "page1": http_connections_page_one,
        "page2": http_connections_page_two,
        "page3": http_connections_page_three,
        "index": http_connections_index
    }

    return visited_page

def get_top_data(adress, user, pdw):
    """ Return data from top command """
    client = connect_to_server_ssh(adress, user, pdw)
    stdin, stdout_top, stderr = client.exec_command('top -n1 -b ')
    line_top = stdout_top.readlines()
    top = ''.join(line_top)
    print(stdin, stderr)
    print(top)

def get_process_running(adress, user, pdw):
    """ Return a map of all process running with their processor consumption and name """
    client = connect_to_server_ssh(adress, user, pdw)
    stdin, stdout_top, stderr = client.exec_command("top -n1 -b | awk "+"'"+"BEGIN {line=0;}{line++;if(line>7){print $1,$9,$12}}"+"'")
    line_top = stdout_top.readlines()
    top = ''.join(line_top)
    top=top.replace("\n"," ")
    top=top.split(" ")
    process={}
    for i in range(0, len(top)-1):
        if i%3==0:
            process[top[i]] = [top[i+1],top[i+2]]

    return process

def get_processor_used(adress, user, pdw):
    """ Return a the percentage of the processor used """
    client = connect_to_server_ssh(adress, user, pdw)
    stdin, stdout_top, stderr = client.exec_command("top -n1 -b | awk "+"'"+"BEGIN {line=0;}{line++;if(line==3){print $8}}"+"'")
    line_top = stdout_top.readlines()
    top = ''.join(line_top)
    top=top.replace("\n","")

    return top

def get_memory_total(adress, user, pdw):
    """ Return a the total memory in Kb """
    client = connect_to_server_ssh(adress, user, pdw)
    stdin, stdout_top, stderr = client.exec_command("free | awk "+"'"+"BEGIN {line=0;}{line++;if(line==2){print $2}}"+"'")
    line_top = stdout_top.readlines()
    top = ''.join(line_top)
    top=top.replace("\n","")

    return int(top)

def get_memory_used(adress, user, pdw):
    """ Return a the memory used in Kb """
    client = connect_to_server_ssh(adress, user, pdw)
    stdin, stdout_top, stderr = client.exec_command("free | awk "+"'"+"BEGIN {line=0;}{line++;if(line==3){print $2}}"+"'")
    line_top = stdout_top.readlines()
    top = ''.join(line_top)
    top=top.replace("\n","")

    return int(top)


def get_memory_free(adress, user, pdw):
    """ Return a the memory free in Kb """
    client = connect_to_server_ssh(adress, user, pdw)
    stdin, stdout_top, stderr = client.exec_command("free | awk "+"'"+"BEGIN {line=0;}{line++;if(line==4){print $2}}"+"'")
    line_top = stdout_top.readlines()
    top = ''.join(line_top)
    top=top.replace("\n","")

    return int(top)

def get_memory_shared(adress, user, pdw):
    """ Return a the memory shared in Kb """
    client = connect_to_server_ssh(adress, user, pdw)
    stdin, stdout_top, stderr = client.exec_command("free | awk "+"'"+"BEGIN {line=0;}{line++;if(line==5){print $2}}"+"'")
    line_top = stdout_top.readlines()
    top = ''.join(line_top)
    top=top.replace("\n","")

    return int(top)

def get_memory_buff_cache(adress, user, pdw):
    """ Return a the memory buff/cache in Kb """
    client = connect_to_server_ssh(adress, user, pdw)
    stdin, stdout_top, stderr = client.exec_command("free | awk "+"'"+"BEGIN {line=0;}{line++;if(line==6){print $2}}"+"'")
    line_top = stdout_top.readlines()
    top = ''.join(line_top)
    top=top.replace("\n","")

    return int(top)

def get_memory_available(adress, user, pdw):
    """ Return a the memory available in Kb """
    client = connect_to_server_ssh(adress, user, pdw)
    stdin, stdout_top, stderr = client.exec_command("free | awk "+"'"+"BEGIN {line=0;}{line++;if(line==7){print $2}}"+"'")
    line_top = stdout_top.readlines()
    top = ''.join(line_top)
    top=top.replace("\n","")

    return int(top)

def get_cpu_model_name(adress, user, pdw):
    """ Return a the name of the processor """
    client = connect_to_server_ssh(adress, user, pdw)
    stdin, stdout_cpu, stderr = client.exec_command("cat /proc/cpuinfo | grep model\ name | awk "+"'"+"{$1=$2=$3="+'""'+";print $0}"+"'")
    line_cpu = stdout_cpu.readlines()
    cpu = ''.join(line_cpu)
    cpu=cpu.replace("   ","")

    return cpu

def get_cache_size(adress, user, pdw):
    """ Return a the cache size of the processor """
    client = connect_to_server_ssh(adress, user, pdw)
    stdin, stdout_cpu, stderr = client.exec_command("cat /proc/cpuinfo | grep cache\ size | awk "+"'"+"{$1=$2=$3=$5="+'""'+";print $0}"+"'")
    line_cpu = stdout_cpu.readlines()
    cpu = ''.join(line_cpu)
    cpu=cpu.replace("   ","")

    return int(cpu)

def get_cpu_frequency(adress, user, pdw):
    """ Return a the frequency of the processor """
    client = connect_to_server_ssh(adress, user, pdw)
    stdin, stdout_cpu, stderr = client.exec_command("cat /proc/cpuinfo | grep cpu\ MHz | awk "+"'"+"{$1=$2=$3="+'""'+";print $0}"+"'")
    line_cpu = stdout_cpu.readlines()
    cpu = ''.join(line_cpu)
    cpu=cpu.replace("   ","")
    cpu=cpu.replace("\n","")

    return float(cpu)

def get_number_of_cores(adress, user, pdw):
    """ Return a the number of cores of the processor """
    client = connect_to_server_ssh(adress, user, pdw)
    stdin, stdout_cpu, stderr = client.exec_command("cat /proc/cpuinfo | grep cpu\ cores | awk "+"'"+"{$1=$2=$3="+'""'+";print $0}"+"'")
    line_cpu = stdout_cpu.readlines()
    cpu = ''.join(line_cpu)
    cpu=cpu.replace("   ","")
    cpu=cpu.replace("\n","")

    return int(cpu)


def get_number_of_connexion_per_ip_addr(adress, user, pdw):
    """ Return a map of the number of connexion per ip address """
    client = connect_to_server_ssh(adress, user, pdw)
    stdin, stdout_log, stderr = client.exec_command("cat /var/log/apache2/access.log | awk "+"'"+ "{print $1}"+"'")
    line_log = stdout_log.readlines()
    log = ''.join(line_log)

    log=log.replace("\n"," ")
    log=log.split(" ")
    ip_addr={}
    for i in range(0, len(log)-1):
        if (log[i] in ip_addr):
            ip_addr[log[i]] += 1
        else :
            ip_addr[log[i]] = 1

    return ip_addr

def get_connexion_per_hour(adress, user, pdw):
    """ Return a map of the number of connexion per hour """
    client = connect_to_server_ssh(adress, user, pdw)
    stdin, stdout_log, stderr = client.exec_command("cat /var/log/apache2/access.log | awk "+"'"+ "{print $4}"+"'")
    line_log = stdout_log.readlines()
    log = ''.join(line_log)
    log=log.replace("[","")
    log=log.replace(":"," ")
    log=log.replace("/"," ")
    log=log.replace("\n"," ")
    log=log.split(" ")
    connexion={}
    for i in range(0, len(log)-1):
        if i%6==0:
            date_connexion=log[i]+" "+log[i+1]+" "+log[i+2]+" "+log[i+3]
            if (date_connexion in connexion):
                connexion[date_connexion] += 1
            else :
                connexion[date_connexion] = 1
    return connexion

def get_connexion_404_per_hour(adress, user, pdw):
    """ Return a map of the number of connexion that failed per hour """
    client = connect_to_server_ssh(adress, user, pdw)
    stdin, stdout_log, stderr = client.exec_command("cat /var/log/apache2/access.log | grep 404 |awk "+"'"+ "{print $4}"+"'")
    line_log = stdout_log.readlines()
    log = ''.join(line_log)
    log=log.replace("[","")
    log=log.replace(":"," ")
    log=log.replace("/"," ")
    log=log.replace("\n"," ")
    log=log.split(" ")
    connexion={}
    for i in range(0, len(log)-1):
        if i%6==0:
            date_connexion=log[i]+" "+log[i+1]+" "+log[i+2]+" "+log[i+3]
            if (date_connexion in connexion):
                connexion[date_connexion] += 1
            else :
                connexion[date_connexion] = 1
    return connexion

def get_connexion_404_rate_per_hour(adress, user, pdw):
    """ Return a map of the percentage of connexion that failed per hour """
    connexion_total=get_connexion_per_hour(adress, user, pdw)
    connexion_404=get_connexion_404_per_hour(adress, user, pdw)
    connexion_rate_404={}
    for i in connexion_total:
        if (i in connexion_404):
            connexion_rate_404[i]= "%.2f" % (connexion_404[i]/connexion_total[i])
        else:
            connexion_rate_404[i]=0
    return connexion_rate_404

def get_number_of_connexion_404_per_ip_addr(adress, user, pdw):
    """ Return a map of the number of connexion that failed per ip address """
    client = connect_to_server_ssh(adress, user, pdw)
    stdin, stdout_log, stderr = client.exec_command("cat /var/log/apache2/access.log | grep 404 | awk "+"'"+ "{print $1}"+"'")
    line_log = stdout_log.readlines()
    log = ''.join(line_log)

    log=log.replace("\n"," ")
    log=log.split(" ")
    ip_addr={}
    for i in range(0, len(log)-1):
        if (log[i] in ip_addr):
            ip_addr[log[i]] += 1
        else :
            ip_addr[log[i]] = 1

    return ip_addr

def get_connexion_404_rate_per_ip_addr(adress, user, pdw):
    """ Return a map of the percentage of connexion that failed per ip address """
    connexion_total=get_number_of_connexion_per_ip_addr(adress, user, pdw)
    connexion_404=get_number_of_connexion_404_per_ip_addr(adress, user, pdw)
    connexion_rate_404={}
    for i in connexion_total:
        if (i in connexion_404):
            connexion_rate_404[i]= "%.2f" % (connexion_404[i]/connexion_total[i])
        else:
            connexion_rate_404[i]=0

    return connexion_rate_404

def test_connexion(adress, user, pdw):
    try:
        connect_to_server_ssh(adress, user, pdw)
        return True
    except ( BadHostKeyException,AuthenticationException, SSHException, socket.error) as e:
        return False
