from colorama import Fore
from autogpt.config.ai_config import AIConfig
from autogpt.config.config import Config
from autogpt.logs import logger
from autogpt.promptgenerator import PromptGenerator
from autogpt.config import Config
from autogpt.setup import prompt_user
from autogpt.utils import clean_input

CFG = Config()


def get_prompt() -> str:
    """
    This function generates a prompt string that includes various constraints,
        commands, resources, and performance evaluations.

    Returns:
        str: The generated prompt string.
    """

    # Initialize the Config object
    cfg = Config()

    # Initialize the PromptGenerator object
    prompt_generator = PromptGenerator()

    # Add constraints to the PromptGenerator object
    prompt_generator.add_constraint(
        "~4000 word limit for short term memory. Your short term memory is short, so"
        " immediately save important information to files."
    )
    prompt_generator.add_constraint(
        "If you are unsure how you previously did something or want to recall past"
        " events, thinking about similar events will help you remember."
    )
    prompt_generator.add_constraint("No user assistance")
    prompt_generator.add_constraint(
        'You always have to specify a command. Only use commands from the list of valid commands listed in '
        'double quotes e.g. "command name", else you get errors.'
    )

    prompt_generator.add_constraint(
        'If you get an error while executing a command from the command list'
        'assume that the command failed, and verify if possible'
    )

    disabled = [("Google Search", "google", {"input": "<search>"}),
                (
                    "Browse Website",
                    "browse_website",
                    {"url": "<url>", "question": "<what_you_want_to_find_on_website>"},
                ),
                (
                    "Start GPT Agent",
                    "start_agent",
                    {"name": "<name>", "task": "<short_task_desc>", "prompt": "<prompt>"},
                ),
                (
                    "Message GPT Agent",
                    "message_agent",
                    {"key": "<key>", "message": "<message>"},
                ),
                ("List GPT Agents", "list_agents", {}),
                ("Delete GPT Agent", "delete_agent", {"key": "<key>"}),
                (
                    "Clone Repository",
                    "clone_repository",
                    {"repository_url": "<url>", "clone_path": "<directory>"},
                )]

    # Define the command list
    commands = [
        ("Create file with new content", "create_file", {"file": "<file>", "text": "<text>"}),
        ("Replace file with new content", "replace_file", {"file": "<file>", "text": "<text>"}),
        ("Read text from file", "read_file", {"file": "<file>"}),
        ("Append text to end of file", "append_to_file", {"file": "<file>", "text": "<text>"}),
        ("Delete file", "delete_file", {"file": "<file>"}),
        (
            "Recursively list all files starting with <directory>, use . as <directory> to list all files ",
            "search_files",
            {"directory": "<directory>"}),
        (
            "Show workspace state, for python files the signatures of implemented classes and functions are shown",
            "show_workspace_state",
            {}
        ),
        (
            "Patch a file with python code using the provided <python code>,"
            " existing code in the file is preserved when possible but the provided code has precedence",
            "patch_python_file",
            {"file": "<file>", "code": "<python code>"}
        ),
        ("Evaluate code and get suggestions and comments", "evaluate_code", {"code": "<full_code_string>"}),
        (
            "Get improved code to consider as replacement code",
            "improve_code",
            {"suggestions": "<list_of_suggestions>", "code": "<full_code_string>"},
        ),
        (
            "Get test code for testing code with specified focus "
            "(if you want to run it you need to write the result to a file first)",
            "write_tests",
            {"code": "<full_code_string>", "focus": "<list_of_focus_areas>"},
        ),
        ("Execute a python file (a new python file can be created with the command write_to_file)",
         "execute_python_file", {"file": "<file>"}),
        ("Generate an image jpg file from prompt", "generate_image", {"prompt": "<prompt>", "file": "<prompt>"})
    ]

    # ("Send Tweet", "send_tweet", {"text": "<text>"}),

    # Only add the audio to text command if the model is specified
    if cfg.huggingface_audio_to_text_model:
        commands.append(
            (
                "Convert Audio to text",
                "read_audio_from_file",
                {"file": "<file>"}
            ),
        )

    # Only add shell command to the prompt if the AI is allowed to execute it
    if cfg.execute_local_commands:
        commands.append(
            (
                "Execute Shell Command, non-interactive commands only",
                "execute_shell",
                {"command_line": "<command_line>"},
            ),
        )

    # Add these command last.
    commands.append(
        ("Do Nothing", "do_nothing", {}),
    )
    commands.append(
        ("Task Complete (Shutdown)", "task_complete", {"reason": "<reason>"}),
    )

    # Add commands to the PromptGenerator object
    for command_label, command_name, args in commands:
        prompt_generator.add_command(command_label, command_name, args)

    # Add resources to the PromptGenerator object
    # prompt_generator.add_resource(
    #    "Internet access for searches and information gathering."
    # )
    prompt_generator.add_resource("Long Term memory management.")
    # prompt_generator.add_resource(
    #    "GPT-3.5 powered Agents for delegation of simple tasks."
    # )
    prompt_generator.add_resource("File input and output.")

    # Add performance evaluations to the PromptGenerator object
    prompt_generator.add_performance_evaluation(
        "When specifying commands to be performed, make sure to verify the result. "
        "If you get errors expect that the command has failed"
    )
    prompt_generator.add_performance_evaluation(
        "Continuously review and analyze your actions to ensure you are performing to"
        " the best of your abilities."
    )
    prompt_generator.add_performance_evaluation(
        "Constructively self-criticize your big-picture behavior constantly, and make sure you stay "
        "focused on solving the assignment efficiently."
    )
    prompt_generator.add_performance_evaluation(
        "Reflect on past decisions and strategies to refine your approach and to stay focused on progress."
    )
    prompt_generator.add_performance_evaluation(
        "Be effective, focus on outcome and keep it simple. "
        "Aim to complete the goals using the least number of steps."
    )
    prompt_generator.add_performance_evaluation(
        "Reflect on your progress and make sure you are producing results in the workspace."
    )

    prompt_generator.add_performance_evaluation(
        "Remember to keep the workspace tidy and delete unnecessary files."
    )

    # Generate the prompt string
    return prompt_generator.generate_prompt_string()


def construct_prompt() -> str:
    """Construct the prompt for the AI to respond to

    Returns:
        str: The prompt string
    """
    config = AIConfig.load(CFG.ai_settings_file)
    if CFG.skip_reprompt and config.ai_name:
        logger.typewriter_log("Name :", Fore.GREEN, config.ai_name)
        logger.typewriter_log("Role :", Fore.GREEN, config.ai_role)
        logger.typewriter_log("Goals:", Fore.GREEN, f"{config.ai_goals}")
    elif config.ai_name:
        logger.typewriter_log(
            "Welcome back! ",
            Fore.GREEN,
            f"Would you like me to return to being {config.ai_name}?",
            speak_text=True,
        )
        should_continue = clean_input(
            f"""Continue with the last settings?
Name:  {config.ai_name}
Role:  {config.ai_role}
Goals: {config.ai_goals}
Continue (y/n): """
        )
        if should_continue.lower() == "n":
            config = AIConfig()

    if not config.ai_name:
        config = prompt_user()
        config.save(CFG.ai_settings_file)

    # Get rid of this global:
    global ai_name
    ai_name = config.ai_name

    return config.construct_full_prompt()
