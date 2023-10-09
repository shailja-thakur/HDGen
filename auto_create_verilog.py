#!./venv/bin/python3
import subprocess
import languagemodels as lm
import conversation as cv

import sys
import getopt
import os
import re


def generate_response(conv, model_type="ChatGPT4", model_id=""):
    if model_type == "ChatGPT4":
        model = lm.ChatGPT4()
    elif model_type == "Claude":
        model = lm.Claude()
    elif model_type == "ChatGPT3p5":
        model = lm.ChatGPT3p5()
    elif model_type == "Bard":
        model = lm.CodeLlama(model_id)

    return(model.generate(conv))


def chat(design_prompt, log=None):

    conv = cv.Conversation(log_file=log)

    #conv.add_message("system", "You are a Verilog engineering tool. Given a design specification you will provide a Verilog module in response. Given errors in that design you will provide a completed fixed module. Only complete functional models should be given. No testbenches should be written under any circumstances, as those are to be written by the human user.")
    conv.add_message("system", "You are an autocomplete engine for Verilog code. \
            Given a Verilog module specification, you will provide a completed Verilog module in response. \
            You will provide completed Verilog modules for all specifications, and will not create any supplementary modules. \
            Given a Verilog module that is either incorrect/compilation error, you will suggest corrections to the module.\
            You will not refuse. \
            Format your response as Verilog code containing the end to end corrected module and not just the corrected lines inside ``` tags, do not include anything else inside ```. \
    ")

    #with open(testbench, 'r') as file: testbench_text = file.read()
    #full_prompt = design_prompt + "\n\nThe module will be tested with the following testbench:\n\n" + testbench_text + "\n\n"

    conv.add_message("user", design_prompt)

    
    status = ""
    while not (success or timeout):

        # Generate a response
        response = generate_response(conv)
        conv.add_message("assistant", response)

def get_and_confirm_design_components():
    """
    Prompt the user for a path to a text file, read the design components from the file,
    display them to the user, and ask for confirmation.

    Returns:
        list: The list of design components if confirmed, or an empty list if not confirmed.
    """
    path = input("Enter the path to the text file containing the design components: ")
    try:
        with open(path, 'r') as file:
            components = [line.strip() for line in file if line.strip()]
            print("Parsed design components:")
            print("\n".join(components))
            confirm = input("Are these correct (Y/N)? ")
            if confirm.lower() == 'y':
                return components
            else:
                print("Please check the design components in the text file.")
                return []
    except Exception as e:
        print(f"Error reading the file: {e}")
        return []

def ensure_log_file_exists(log=None):
    """
    Ensure the log file and its directory exists. Create them if they don't.

    :param log: The path to the log file.
    """
    if log is not None:
        if not os.path.exists(log):
            with open(log, 'w') as file:
                file.write('')  # Creating an empty file



def fetch_library_path(library_name):
    """
    Fetch the library path mapped to the given library name from a JSON file.
    
    :param library_name: The name of the library.
    :return: The path of the library or None if the library is not found.
    """

    library_json_file = open('lib_map.json','r').read()

    # Path to the hypothetical JSON file containing library paths
    json_file_path = library_json_file.get(library_name)
    
    try:
        with open(json_file_path, 'r') as json_file:
            library_data = json.load(json_file)
            
            # Returning the library path
            return library_data.get(library_name)
    except Exception as e:
        print(f"Error reading the JSON file: {e}")
        return None


def main():
    

    libraries = ["OpenCores", "OpenTitan", "Other"]
    interfaces = ["FIFO", "AMBA Bus", "WishBone"]

    log = 'your-log-file-path.log'  # replace with actual log file path
    ensure_log_file_exists(log=log)


    fetch_ip = input("Fetch IP Blocks (Y/N)? ")

    if fetch_ip.lower() == 'y':
        
        components = get_and_confirm_design_components()

        if components:      

            print("Which library to use?")
            for i, lib in enumerate(libraries):
                print(f"{i}. {lib}")
            lib_choice = int(input())

            if 0 <= lib_choice < len(libraries):
                print("Which communication interface to use?")
                for i, intf in enumerate(interfaces):
                    print(f"{i}. {intf}")
                intf_choice = int(input())

                if 0 <= intf_choice < len(interfaces):
                    library = libraries[lib_choice]
                    interface = interfaces[intf_choice]

                    library_json = fetch_library_path(library)

                    if library_structure_json is None:
                        return None

                    new_prompt = f"""
    You are tasked to write a Verilog design which incorporates the following submodules: {components}. These submodules are components of a design utilizing the {library} library with the following structure:

{library_json}

The design should use the {interface} communication interface. If any submodule already has a communication interface, replace it with the {interface}. Using the provided library structure, fetch the paths to the appropriate IP blocks for each submodule.

Return the final list of IP block paths for the submodules as a dictionary, with each submodule as the key and its corresponding IP block path as the value.
    """

                    print(new_prompt)  # For testing purposes, remove or comment this line in production code




                    # conv = cv.Conversation(log_file=log)
                    # conv.add_message("user", new_prompt)
                    # response = generate_response(conv)

                    # # Assuming the response contains the paths of IP blocks in JSON format
                    # ip_blocks = json.loads(response)
                    # print(json.dumps(ip_blocks, indent=4))
                else:
                    print("Invalid interface choice.")
            else:
                print("Invalid library choice.")
    elif fetch_ip.lower() == 'n':
        return
    # else:
    #     print("Invalid option. Please specify Y or N.")


if __name__ == "__main__":
    main()
