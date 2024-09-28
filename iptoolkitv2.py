import socket
import requests
import ipaddress
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
from colorama import Fore, Style, init
import threading
import subprocess

# Initialize colorama
init(autoreset=True)

# ASCII Art for the IP Toolkit with credits
TOOLKIT_ART = f"""
{Fore.CYAN}###############################################
#                                             #
#          {Fore.YELLOW}____  _____ _______ _____          {Fore.CYAN}#
#         {Fore.YELLOW}|_   \\|_   _|__   __|_   _|         {Fore.CYAN}#
#           {Fore.YELLOW}| |\\ \\ | |    | |    | |           {Fore.CYAN}#
#           {Fore.YELLOW}| | \\ \\| |    | |    | |           {Fore.CYAN}#
#          {Fore.YELLOW}_| |_\\   |_   _| |_  _| |_          {Fore.CYAN}#
#         {Fore.YELLOW}|_____|\\____| |_____|_____|{Fore.CYAN} IP Toolkit #
#                                             #
#        {Fore.MAGENTA}Created by iamgeo1 and mzzzq        {Fore.CYAN}#
#                                             #
{Fore.CYAN}###############################################
"""

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    """Custom request handler to log IP and show information."""
    
    def do_GET(self):
        # Parse the URL
        parsed_path = urlparse(self.path)
        
        if parsed_path.path.startswith('/redirect/'):
            # Log the user's IP address
            user_ip = self.client_address[0]
            print(f"Redirecting {user_ip}...")

            # Get geolocation info for the IP
            geolocation_info = self.get_geolocation(user_ip)

            # Send the user information as a response
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            response_html = f"""
            <html>
                <body>
                    <h1>Your IP: {user_ip}</h1>
                    <h2>Geolocation Information:</h2>
                    <pre>{geolocation_info}</pre>
                    <h3>Redirecting to: {parsed_path.path[10:]}</h3>
                </body>
            </html>
            """
            self.wfile.write(response_html.encode())

            # Redirect to the specified URL
            self.send_response(302)
            self.send_header('Location', parsed_path.path[10:])
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def get_geolocation(self, ip):
        """Get geolocation information for a given IP address."""
        try:
            ip_obj = ipaddress.ip_address(ip)
            if ip_obj.is_private:
                return "Local IP addresses do not have geolocation information."
            else:
                response = requests.get(f"https://ipinfo.io/{ip}/json")
                data = response.json()
                formatted_data = json.dumps(data, indent=4)
                return formatted_data
        except Exception as e:
            return f"Failed to retrieve geolocation information: {str(e)}"

def run_server(port=8000):
    """Run the HTTP server."""
    server_address = ('', port)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    httpd.serve_forever()  # Run the server indefinitely

def start_server_thread():
    """Start the HTTP server in a separate thread."""
    server_thread = threading.Thread(target=run_server, args=(8000,))
    server_thread.daemon = True  # Allow thread to exit when main program does
    server_thread.start()

# Utility class for the IP Toolkit functionalities
class IPToolkit:
    
    def __init__(self):
        pass

    def get_local_ip(self):
        """Get the local IP address of the machine."""
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        return local_ip

    def get_public_ip(self):
        """Retrieve the public IP address using an external service."""
        try:
            response = requests.get('https://api.ipify.org?format=json')
            public_ip = response.json()['ip']
            return public_ip
        except Exception as e:
            return f"Failed to retrieve public IP: {str(e)}"

    def ip_geolocation(self, ip):
        """Get geolocation information for a given IP address."""
        try:
            ip_obj = ipaddress.ip_address(ip)
            if ip_obj.is_private:
                return json.dumps({
                    "IP": str(ip_obj),
                    "Message": "Local IP addresses do not have geolocation information available. They are used within private networks."
                }, indent=4)
            else:
                response = requests.get(f"https://ipinfo.io/{ip}/json")
                data = response.json()
                address = data.get('hostname', 'Unknown') + ', ' + data.get('city', 'Unknown') + ', ' + data.get('region', 'Unknown') + ', ' + data.get('country', 'Unknown')
                formatted_data = {
                    "IP": ip,
                    "Hostname": data.get('hostname', 'N/A'),
                    "City": data.get('city', 'N/A'),
                    "Region": data.get('region', 'N/A'),
                    "Country": data.get('country', 'N/A'),
                    "Location": data.get('loc', 'N/A'),
                    "Postal": data.get('postal', 'N/A'),
                    "Address": address
                }
                return json.dumps(formatted_data, indent=4)
        except Exception as e:
            return f"Failed to retrieve geolocation information: {str(e)}"

    def ip_info(self, ip):
        """Retrieve basic information about an IP address."""
        try:
            ip_obj = ipaddress.ip_address(ip)
            return {
                "IP": str(ip_obj),
                "Version": ip_obj.version,
                "Is Private": ip_obj.is_private,
                "Packed": ip_obj.packed.hex()
            }
        except ValueError:
            return "Invalid IP address format."

    def generate_ngrok_link(self):
        """Generate a Ngrok link."""
        try:
            command = ["ngrok", "http", "8000"]
            subprocess.Popen(command)  # Start the Ngrok tunnel
            return "Ngrok link created! Visit: http://localhost:4040 for the forwarding URL."
        except Exception as e:
            return f"Failed to create Ngrok link: {str(e)}"

    def generate_serveo_link(self):
        """Generate a Serveo.net link."""
        try:
            command = ["ssh", "-R", "80:localhost:8000", "serveo.net"]
            subprocess.Popen(command)  # Start the Serveo tunnel
            return "Serveo link created! Visit: https://<your-serveo-username>.serveo.net"
        except Exception as e:
            return f"Failed to create Serveo link: {str(e)}"

def print_header_footer():
    """Print a colorful header and footer."""
    print(Fore.MAGENTA + "\n" + "=" * 50)
    print(Fore.LIGHTCYAN_EX + "        Welcome to the IP Toolkit!         ")
    print(Fore.LIGHTCYAN_EX + "         Choose an option below:           ")
    print(Fore.MAGENTA + "=" * 50)

def print_menu():
    """Print the menu options with better formatting."""
    print(Fore.BLUE + "1. Get Local IP Address")
    print(Fore.BLUE + "2. Get Public IP Address")
    print(Fore.BLUE + "3. IP Geolocation")
    print(Fore.BLUE + "4. IP Information")
    print(Fore.BLUE + "5. Generate Tunnel Link")
    print(Fore.BLUE + "6. Exit")

def main():
    # Print ASCII art and menu options
    print(TOOLKIT_ART)
    toolkit = IPToolkit()

    # Start the HTTP server thread
    start_server_thread()

    # Menu options for the toolkit
    while True:
        print_header_footer()
        print_menu()

        choice = input(Fore.YELLOW + "\nEnter your choice (1-6): ")

        if choice == '1':
            print(Fore.GREEN + f"\nLocal IP Address: {toolkit.get_local_ip()}\n")
        elif choice == '2':
            print(Fore.GREEN + f"\nPublic IP Address: {toolkit.get_public_ip()}\n")
        elif choice == '3':
            ip = input(Fore.YELLOW + "Enter the IP address for geolocation (e.g., 8.8.8.8): ")
            print(Fore.GREEN + f"Geolocation Information:\n{toolkit.ip_geolocation(ip)}\n")
        elif choice == '4':
            ip = input(Fore.YELLOW + "Enter the IP address for information (e.g., 8.8.8.8): ")
            ip_information = toolkit.ip_info(ip)
            if isinstance(ip_information, dict):
                formatted_info = "\n".join([f"{key}: {value}" for key, value in ip_information.items()])
                print(Fore.GREEN + f"IP Information:\n{formatted_info}\n")
            else:
                print(Fore.RED + f"Error: {ip_information}\n")
        elif choice == '5':
            tunnel_choice = input(Fore.YELLOW + "Choose a tunnel service:\n1. Ngrok\n2. Serveo\nEnter your choice (1-2): ")
            if tunnel_choice == '1':
                ngrok_message = toolkit.generate_ngrok_link()
                print(Fore.GREEN + ngrok_message)
                input(Fore.YELLOW + "Link is ready to send! Press Enter to return to the main menu.")
            elif tunnel_choice == '2':
                serveo_message = toolkit.generate_serveo_link()
                print(Fore.GREEN + serveo_message)
                input(Fore.YELLOW + "Link is ready to send! Press Enter to return to the main menu.")
            else:
                print(Fore.RED + "Invalid choice for tunnel service. Returning to main menu.\n")
        elif choice == '6':
            print(Fore.RED + "Exiting IP Toolkit. Goodbye!\n")
            break
        else:
            print(Fore.RED + "Invalid choice, please try again.\n")

if __name__ == "__main__":
    main()
