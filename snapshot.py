#!/usr/bin/python
import subprocess
import sys
import time
from datetime import datetime
import tarfile
import os


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


SNAP_FLAG = 0
TYPE_FLAG = 0
IP = ''
dw_array = []
bi_array = []
dw_folders = ['DW-ETL', 'ACP', 'Vertica', 'Config']
bi_folders = ['BI-ETL', 'ACP', 'MSTR', 'Config']
single_folders = ['ETL', 'ACP', 'MSTR', 'Vertica', 'Config']

vip = ''
bi_services_array = [["/opt/allot/clearsee/python/bin/supervisorctl status", 'ETL_modules_status'], ["su - dbadmin -c '/opt/vertica/bin/admintools -t view_cluster -x'", "vertica_status"],
                     ["/opt/admin/bin/allottype", "allottype"], ["/etc/init.d/clearsee_snmp status", "clearsee_snmp"],
                     ["/bin/systemctl status ntpd.service", "ntpd"],
                     ["/etc/init.d/rabbitmq-server status", "rabbitmq-server"],
                     ["/etc/init.d/vertica_agent status", "vertica_agent"], ["/etc/init.d/verticad status", "verticad"],
                     ["/usr/bin/psql -U dbadmin -w dbadmin -d central_repository -c 'select * from etl.license_key;'",
                      "license_key"],
                     ['echo printls | /opt/allot/clearsee/etl/pymodules/License/LicenseCLI.py', 'license_details'],
                     ['/bin/systemctl status tomcat.service'], ['netstat -an', 'netstat'],
                     ['/opt/MicroStrategy/home/bin/mstrctl -s IntelligenceServer get-status', 'MSTR_status'],
                     ['df -h', 'df-h'], ['rabbitmqctl list_queues', 'rabbitmqctl_list_queues'],
                     ['rabbitmqctl cluster_status', 'rabbitmqctl_cluster_status'],
                     ['/bin/systemctl status postgresql', 'postgresql_status'],
                     ['/opt/allot/clearsee/etl/admin/monitor.sh -a', 'report-monitor'],
                     ['date', 'sysconfig_clock'],
                     ['cat /etc/profile.d/vertica.sh', 'vertica_clock'], ['cat /etc/odbc.ini', 'odbc_clock']]
dw_services_array = [["/opt/allot/clearsee/python/bin/supervisorctl status", 'ETL_modules_status'], ["su - dbadmin -c '/opt/vertica/bin/admintools -t view_cluster -x'", "vertica_status"],
                     ["/opt/admin/bin/allottype", "allottype"], ["/etc/init.d/clearsee_snmp status", "clearsee_snmp"],
                     ["/bin/systemctl status ntpd.service", "ntpd"],
                     ["/etc/init.d/rabbitmq-server status", "rabbitmq-server"],
                     ["/etc/init.d/vertica_agent status", "vertica_agent"], ["/etc/init.d/verticad status", "verticad"],
                     ["/usr/bin/psql -U dbadmin -w dbadmin -d central_repository -c 'select * from etl.license_key;'",
                      "license_key"],
                     ['echo printls | /opt/allot/clearsee/etl/pymodules/License/LicenseCLI.py', 'license_details'],
                     ['/bin/systemctl status tomcat.service'], ['netstat -an', 'netstat'],
                     ['/opt/MicroStrategy/home/bin/mstrctl -s IntelligenceServer get-status', 'MSTR_status'],
                     ['df -h', 'df-h'], ['rabbitmqctl list_queues', 'rabbitmqctl_list_queues'],
                     ['rabbitmqctl cluster_status', 'rabbitmqctl_cluster_status'],
                     ['/bin/systemctl status postgresql', 'postgresql_status'],
                     ['/opt/allot/clearsee/etl/admin/monitor.sh -a', 'report-monitor'],
                     ['date', 'sysconfig_clock'],
                     ['cat /etc/profile.d/vertica.sh', 'vertica_clock'], ['cat /etc/odbc.ini', 'odbc_clock']]
single_services_array = [["/opt/allot/clearsee/python/bin/supervisorctl status", 'ETL_modules_status'], ["su - dbadmin -c '/opt/vertica/bin/admintools -t view_cluster -x'", "vertica_status"],
                         ["/opt/admin/bin/allottype", "allottype"],
                         ["/etc/init.d/clearsee_snmp status", "clearsee_snmp"],
                         ["/bin/systemctl status ntpd.service", "ntpd"],
                         ["/etc/init.d/rabbitmq-server status", "rabbitmq-server"],
                         ["/etc/init.d/vertica_agent status", "vertica_agent"],
                         ["/etc/init.d/verticad status", "verticad"], [
                             "/usr/bin/psql -U dbadmin -w dbadmin -d central_repository -c 'select * from etl.license_key;'",
                             "license_key"],
                         ["/usr/bin/psql -U dbadmin -w dbadmin -d central_repository -c 'select * from etl.nodes;'",
                          "BI_Primary"],
                         ["/opt/vertica/bin/vsql -U dbadmin -w dbadmin -d clearseedwh -c 'select * from nodes;'",
                          "DW_primary"],
                         ['echo printls | /opt/allot/clearsee/etl/pymodules/License/LicenseCLI.py', 'license_details'],
                         ['/bin/systemctl status tomcat.service', 'tomcat'], ['netstat -an', 'netstat'],
                         ['/opt/MicroStrategy/home/bin/mstrctl -s IntelligenceServer get-status', 'MSTR_status'],
                         ['df -h', 'df-h'], ['rabbitmqctl list_queues', 'rabbitmqctl_list_queues'],
                         ['rabbitmqctl cluster_status', 'rabbitmqctl_cluster_status'],
                         ['/bin/systemctl status postgresql', 'postgresql_status'],
                         ['/opt/allot/clearsee/etl/admin/monitor.sh -a', 'report-monitor'],
                         ['date', 'sysconfig_clock'],
                         ['cat /etc/profile.d/vertica.sh', 'vertica_clock'], ['cat /etc/odbc.ini', 'odbc_clock']]



def set_ip(ip_addr):
   global IP
   IP = ip_addr

def set_snap_flag(snap_type):
   global SNAP_FLAG
   SNAP_FLAG = snap_type

def set_type_flag(cs_type):
   global TYPE_FLAG
   TYPE_FLAG = cs_type



def analysis_hosts():
    with open("/etc/hosts", "r") as ins:
        for line in ins:
            if "dw" in line and "ha" not in line:
                dw_array.append(line.split(' ', 1)[0])
            elif "bi" in line and "ha" not in line and "127.0.0.1" not in line and "ipv" not in line and "drbd" not in line and "cs-bi" not in line:
                bi_array.append(line.split(' ', 1)[0])
            elif "ipv" in line:
                vip = line.split(' ', 1)[0]


def os_execute(cmd, host=None):
    if host:
        cmd = "ssh -q root@{ip} \"{cmd}\"".format(ip=host, cmd=cmd)

    output, err = subprocess.Popen(cmd, shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   preexec_fn=os.setpgrp).communicate()
    if err:
        part1 = """ssh -q root@{ip} echo """.format(ip=IP)
        part2 = "\"{error}\"".format(error=err)
        logerr = part1 + part2.replace('\n', '').replace('`', '\'') + " >> /data/Snapshot/snapshotlog.log"
        print logerr
        subprocess.Popen(logerr, shell=True, stdout=subprocess.PIPE)


def check_type():
    if (len(bi_array) > int(1)):
        set_type_flag(1)


def create_folder(folder):
    command = 'mkdir %s' % folder
    os_execute(cmd=command, host=IP)
    time.sleep(1)


def zip_snapshot(type_index):
    file_name = type_index + '-Snapshot-' + str(datetime.now().year) + str('%02d' % datetime.now().month) + str(
        datetime.now().day)
    command = 'tar cvzf /opt/admin/' + file_name + '.tgz' + ' /data/Snapshot/'
    os_execute(cmd=command, host=IP)
    time.sleep(1)


def zip_cluster_snapshot(type_index):
    file_name = type_index + '-Snapshot-' + str(datetime.now().year) + str('%02d' % datetime.now().month) + str(
        datetime.now().day)
    command = 'tar cvzf /opt/admin/' + file_name + '.tgz' + ' /opt/admin/Cluster-Snapshot/'
    os_execute(cmd=command, host=IP)
    time.sleep(1)


def logger(path, target):
    if (SNAP_FLAG == 0):
        # print ("the path is %s and target is %s" % (path,target))
        command = """find {find_path} -name '*.log' | xargs -d \'\\n\' cp -t /data/Snapshot/{dst}""".format(
            find_path=path, dst=target)
        # print ("the  before popen cmd is  %s" % command)
        os_execute(cmd=command, host=IP)

    else:
        command = """find {find_path} -name '*.log*' | xargs -d \'\\n\' cp -t  /data/Snapshot/{dst}""".format(
            find_path=path, dst=target)
        os_execute(cmd=command, host=IP)
    time.sleep(1)


def log_command(command, filename):
    full_command = command + ' &> ' + filename
    os_execute(cmd=full_command, host=IP)
    time.sleep(1)


def move_to_vip():
    date = str(datetime.now().year) + str('%02d' % datetime.now().month) + str(datetime.now().day)
    command = """rsync -avz --remove-source-files -e ssh "*Snapshot-{date_snap}'*' root@{primary}:/opt/admin/Cluster-Snapshot/""".format(
        date_snap=date, primary=vip)
    os_execute(cmd=command, host=IP)
    time.sleep(1)


def clean_node():
    command = 'rm -rf /data/Snapshot/'
    os_execute(cmd=command, host=IP)
    time.sleep(1)


def single_snapshot():
    print('######################### Start Single Node Snapshot #########################')
    show_system_ips()
    set_ip('localhost')
    # Create folder
    create_folder('/data/Snapshot')
    time.sleep(1)

    os_execute(cmd="touch /data/Snapshot/snapshotlog.log", host=IP)

    base_dir = '/data/Snapshot/'
    for j in single_folders:
        sub_folder = j
        full_path = os.path.join(base_dir, sub_folder)
        create_folder(full_path)
        time.sleep(1)

    # Vertica logs
    print(bcolors.BOLD + "Collecting Vertica logs : " + bcolors.WARNING + "In Progress" + bcolors.ENDC)
    logger('/opt/vertica/', 'Vertica')
    time.sleep(1)
    logger('/opt/vertica_catalog/', 'Vertica')
    time.sleep(1)
    print(bcolors.BOLD + "Collecting Vertica logs: " + bcolors.OKGREEN + "Done" + bcolors.ENDC)

    # Log services
    print(bcolors.BOLD + "Collecting Config logs : " + bcolors.WARNING + "In Progress" + bcolors.ENDC)
    base_dir = '/data/Snapshot/Config'
    for k in single_services_array:
        service = k[0]
        log_file = k[1] + '.log'
        full_path = os.path.join(base_dir, log_file)
        log_command(service, full_path)
        time.sleep(1)
    print(bcolors.BOLD + "Collecting Config logs: " + bcolors.OKGREEN + "Done" + bcolors.ENDC)

    # MSTR logs
    print(bcolors.BOLD + "Collecting MSTR logs: " + bcolors.WARNING + "In Progress" + bcolors.ENDC)
    logger('/opt/MicroStrategy/', 'MSTR')
    time.sleep(1)
    print(bcolors.BOLD + "Collecting MSTR logs: " + bcolors.OKGREEN + "Done" + bcolors.ENDC)

    # ETL logs
    print(bcolors.BOLD + "Collecting ETL logs: " + bcolors.WARNING + "In Progress" + bcolors.ENDC)
    logger('/opt/allot/clearsee/etl/', 'ETL')
    time.sleep(1)
    print(bcolors.BOLD + "Collecting ETL logs: " + bcolors.OKGREEN + "Done" + bcolors.ENDC)

    # ACP logs
    print(bcolors.BOLD + "Collecting ACP logs: " + bcolors.WARNING + "In Progress" + bcolors.ENDC)
    logger('/usr/', 'ACP')
    time.sleep(1)
    logger('/opt/tomcat/logs/', 'ACP')
    time.sleep(1)
    logger('/var/', 'ACP')
    time.sleep(1)
    logger('/root/', 'ACP')
    time.sleep(1)
    logger('/opt/allot/clearsee/python/', 'ACP')
    time.sleep(1)
    logger('/opt/allot/clearsee/install/', 'ACP')
    time.sleep(1)
    logger('/opt/allot/log/', 'ACP')
    print(bcolors.BOLD + "Collecting ACP logs: " + bcolors.OKGREEN + "Done" + bcolors.ENDC)

    time.sleep(1)

    # ZIP
    print ('Finalize Single-Node Snapshot')
    time.sleep(1)
    print(bcolors.BOLD + "Zip Snapshot: " + bcolors.WARNING + "In Progress" + bcolors.ENDC)
    zip_snapshot('Single-Node')
    print(bcolors.BOLD + "Zip Snapshot: " + bcolors.OKGREEN + "Done" + bcolors.ENDC)
    time.sleep(1)

    # Clean
    clean_node()
    time.sleep(1)

    print(bcolors.BOLD + "CS SINGLE Snapshot was created " + bcolors.OKGREEN + "Successfuly" + bcolors.ENDC + ": Can be found under - " + vip + ":/opt/admin/")
    print('######################### Finish #########################')



def bi_cluster_snapshot():
    print('Start bi snapshot nodes')
    index = 1
    for i in bi_array:
        set_ip(i)
        print('Snapshot ' + 'bi-' + str(index) + ' IP : ' + IP)

        # Create folder
        create_folder('/data/Snapshot')
        time.sleep(1)

        os_execute(cmd="touch /data/Snapshot/snapshotlog.log", host=IP)

        base_dir = '/data/Snapshot/'
        for j in bi_folders:
            sub_folder = j
            full_path = os.path.join(base_dir, sub_folder)
            create_folder(full_path)
            time.sleep(1)

        # Log services
        print(
                    bcolors.BOLD + "Collecting Services Status And Config Files: " + bcolors.WARNING + "In Progress" + bcolors.ENDC)
        base_dir = '/data/Snapshot/Config'
        for k in bi_services_array:
            service = k[0]
            log_file = k[1] + '.log'
            full_path = os.path.join(base_dir, log_file)
            log_command(service, full_path)
            time.sleep(1)
        print(bcolors.BOLD + "Collecting Services Status And Config Files: " + bcolors.OKGREEN + "Done" + bcolors.ENDC)

        # MSTR logs
        print(bcolors.BOLD + "Collecting MSTR Logs: " + bcolors.WARNING + "In Progress" + bcolors.ENDC)
        logger('/opt/MicroStrategy/', 'MSTR')
        time.sleep(1)
        print(bcolors.BOLD + "Collecting MSTR Logs: " + bcolors.OKGREEN + "Done" + bcolors.ENDC)

        # ETL logs
        print(bcolors.BOLD + "Collecting ETL Logs: " + bcolors.WARNING + "In Progress" + bcolors.ENDC)
        logger('/opt/allot/clearsee/etl/', 'BI-ETL')
        time.sleep(1)
        print(bcolors.BOLD + "Collecting ETL Logs: " + bcolors.OKGREEN + "Done" + bcolors.ENDC)

        # ACP logs
        print(bcolors.BOLD + "Collecting ACP Logs: " + bcolors.WARNING + "In Progress" + bcolors.ENDC)
        logger('/usr/', 'ACP')
        time.sleep(1)
        logger('/opt/tomcat/logs/', 'ACP')
        time.sleep(1)
        logger('/var/', 'ACP')
        time.sleep(1)
        logger('/root/', 'ACP')
        time.sleep(1)
        logger('/opt/allot/', 'ACP')
        print(bcolors.BOLD + "Collecting ACP Logs: " + bcolors.OKGREEN + "Done" + bcolors.ENDC)

    time.sleep(100)
    index = 1
    for i in bi_array:
        IP = i
        # ZIP
        print ('ZIP ' + 'BI-' + str(index) + ' Snapshot ')
        zip_snapshot('bi-' + str(index))
        print(bcolors.BOLD + "Zip BI-" + str(index) + ": " + bcolors.WARNING + "In Progress" + bcolors.ENDC)
        time.sleep(5)
        print(bcolors.BOLD + "Zip BI-" + str(index) + ": " + bcolors.OKGREEN + "Done" + bcolors.ENDC)
        index = index + 1

    time.sleep(100)
    index = 1
    for i in bi_array:
        set_ip(i)
        # Move to VIP
        print(bcolors.BOLD + "Move bi-" + str(index) + " to vip : " + bcolors.WARNING + "In Progress" + bcolors.ENDC)
        move_to_vip()
        time.sleep(1)
        print(bcolors.BOLD + "Move bi-" + str(index) + " to vip : " + bcolors.OKGREEN + "Done" + bcolors.ENDC)
        index = index + 1
    time.sleep(60)

    print(bcolors.BOLD + "BI Snapshot Created " + bcolors.OKGREEN + "Successfuly" + ": PATH - " + vip + ":/opt/admin/" + bcolors.ENDC)



def dw_cluster_snapshot():
    print('Start DW snapshot nodes')
    show_system_ips()
    index = 1
    for i in dw_array:
        set_ip(i)
        print('Snapshot ' + 'dw-' + str(index) + ' IP : ' + IP)

        # Create folder
        create_folder('/data/Snapshot')
        time.sleep(1)

        os_execute(cmd="touch /data/Snapshot/snapshotlog.log", host=IP)
        base_dir = '/data/Snapshot/'
        for j in dw_folders:
            sub_folder = j
            full_path = os.path.join(base_dir, sub_folder)
            create_folder(full_path)
            time.sleep(1)

        # Vertica logs
        print ('Collecting Vertica logs ...')
        logger('/opt/vertica/', 'Vertica')
        time.sleep(1)
        logger('/opt/vertica_catalog/', 'Vertica')
        time.sleep(1)
        print(bcolors.BOLD + "Vertica logs was collected " + bcolors.OKGREEN + "Successfuly" + bcolors.ENDC)

        # Log services
        print(
                    bcolors.BOLD + "Collecting Services Status And Config Files: " + bcolors.WARNING + "In Progress" + bcolors.ENDC)
        base_dir = '/data/Snapshot/Config'
        for k in dw_services_array:
            service = k[0]
            log_file = k[1] + '.log'
            full_path = os.path.join(base_dir, log_file)
            log_command(service, full_path)
            time.sleep(1)
        print(bcolors.BOLD + "Collecting Services Status And Config Files: " + bcolors.OKGREEN + "Done" + bcolors.ENDC)

        # MSTR logs
        print(bcolors.BOLD + "Collecting MSTR Logs: " + bcolors.WARNING + "In Progress" + bcolors.ENDC)
        logger('/opt/MicroStrategy/', 'MSTR')
        time.sleep(1)
        print(bcolors.BOLD + "Collecting MSTR Logs: " + bcolors.OKGREEN + "Done" + bcolors.ENDC)

        # DW-ETL logs
        print(bcolors.BOLD + "Collecting ETL Logs: " + bcolors.WARNING + "In Progress" + bcolors.ENDC)
        logger('/opt/allot/clearsee/etl/', 'DW-ETL')
        time.sleep(1)
        print(bcolors.BOLD + "Collecting ETL Logs: " + bcolors.OKGREEN + "Done" + bcolors.ENDC)

        # ACP logs
        print(bcolors.BOLD + "Collecting ACP Logs: " + bcolors.WARNING + "In Progress" + bcolors.ENDC)
        logger('/usr/', 'ACP')
        time.sleep(1)
        logger('/opt/tomcat/logs/', 'ACP')
        time.sleep(1)
        logger('/var/', 'ACP')
        time.sleep(1)
        logger('/root/', 'ACP')
        time.sleep(1)
        logger('/opt/allot/', 'ACP')
        print(bcolors.BOLD + "Collecting ACP Logs: " + bcolors.OKGREEN + "Done" + bcolors.ENDC)
        index = index + 1

    time.sleep(100)
    index = 1
    for i in dw_array:
        set_ip(i)
        # ZIP
        print ('ZIP ' + 'dw-' + str(index) + ' Snapshot ')
        zip_snapshot('dw-' + str(index))
        time.sleep(5)
        print(bcolors.BOLD + "Zip Snapshot was finished " + bcolors.OKGREEN + "Successfuly" + bcolors.ENDC)
        index = index + 1

    time.sleep(100)
    index = 1
    for i in dw_array:
        set_ip(i)
        # Move to VIP
        print(bcolors.BOLD + "Move dw-" + str(index) + " to vip : " + bcolors.WARNING + "In Progress" + bcolors.ENDC)
        move_to_vip()
        time.sleep(1)
        print(bcolors.BOLD + "Move dw-" + str(index) + " to vip : " + bcolors.OKGREEN + "Done" + bcolors.ENDC)
        index = index + 1

    time.sleep(60)
    print(
                bcolors.BOLD + "DW Snapshot was finished " + bcolors.OKGREEN + "Successfuly" + ": Can be found under - " + vip + ":/opt/admin" + bcolors.ENDC)


def cluster_snapshot():
    print('######################### Start Cluster Snapshot #########################')

    set_ip(vip)
    create_folder('/opt/admin/Cluster-Snapshot')
    dw_cluster_snapshot()
    bi_cluster_snapshot()
    # Move to VIP
    print(bcolors.BOLD + "finalizing Snapshot :  " + bcolors.WARNING + "In Progress" + bcolors.ENDC)
    # CLEAN
    for i in bi_array:
        IP = i
        clean_node()
        time.sleep(1)
    for j in dw_array:
        IP = j
        clean_node()
        time.sleep(1)
    print(bcolors.BOLD + "finalizing Snapshot :  " + bcolors.OKGREEN + "Done" + bcolors.ENDC)
    print('######################### Finish Cluster Snapshot #########################')



def script_options():
    print(
        "Usage:  snapshot.py [ OPTION ]\n-F, Full Snapshot : Collecting all *.log in  the System incluse *.tgz files,\n-L, Light Snapshot : Snapshot without *.tgz log files\n-q, -help : show help message.\n")


def show_system_ips():
    if (TYPE_FLAG == 0):
        print('CS TYPE: SINGLE NODE')
    else:
        print('CS TYPE: CLUSTER')
        print('VIP IP: ' + str(vip))
        print('BI IPS: ' + str(bi_array))
        print('DW IPS: ' + str(dw_array))


def main():
    # Start
    analysis_hosts()
    check_type()
    try:
        sys.argv[1]
    # Handel out of range exception
    except IndexError:
        script_options()
        return

    # Check input
    if (sys.argv[1] == "-F"):
        set_snap_flag(1)
        if (TYPE_FLAG == 0):
            single_snapshot()
        else:
            cluster_snapshot()
    elif (sys.argv[1] == "-L"):
        set_snap_flag(0)
        if (TYPE_FLAG == 0):
            single_snapshot()
        else:
            cluster_snapshot()

    else:
        script_options()


# END

if __name__ == "__main__":
    main()




