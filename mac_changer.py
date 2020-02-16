import subprocess
import optparse

parser = optparse.OptionParser()


def parser_func():
    """
    Parser to check input arguments 
    """
    parser.add_option(
        "-i",
        "--interface",
        dest="interface",
        help="provide interface to change its mac",
    )
    parser.add_option(
        "-m", "--mac", dest="new_mac", help="provide new mac address to change"
    )

    (options, arguments) = parser.parse_args()

    if not options.interface:
        parser.error("[-] Please provide valid interface, check use --help")
    elif not options.new_mac:
        parser.error("[-] Please provide valid mac address, check use --help")

    return options


def mac_check(interface):
    """
     function to execute the command to fetch output of ifconfig
    """
    ifconfig_result = subprocess.check_output(["ifconfig", interface])
    print(dir(ifconfig_result))
    if ifconfig_result:
        return ifconfig_result
    else:
        return False


# parser.add_option(
#     "-i", "--interface", dest="interface", help="Interface to change its mac address"
# )

# parser.add_option("-m", "--mac", dest="mac", help="New Mac address")

# (options, arguments) = parser.parse_args()


parser_output = parser_func()

ifconfig_result_out = mac_check(parser_output.interface)

if ifconfig_result_out:
    print(ifconfig_result_out.decode("utf-8"))
else:
    print("command not executed")

# interface = options.interface
# new_mac = options.mac

# # if not interface:
# #     parser.error(
# #         "[-1] Please specify the interface to change its mac add, use --help for more information"
# #     )
# # elif not new_mac:
# #     parser.error(
# #         "[-2] Please specify new mac address to change, use --help for more information"
# #     )

# # mac = subprocess.call("ifconfig en1", shell=True)

# # subprocess.checkout will return the output to variable , whereas subprocess.call wont
# ifconfig_result = subprocess.check_output(["ifconfig", options.interface])
# print("irfan")

# print((ifconfig_result).decode("utf-8"))
new_mac = "00:11:22:33:44:55"
interface = "en1"
number = 10
print(
    f"Changing the mac address of {interface} to new mac address {new_mac} by {number} of times"
)

