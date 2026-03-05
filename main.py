import click
import getpass

#Helper functions
from encrypt.encrypt import *

@click.command(
        help=f"""
\n
\n
Options:
  -h, --help    Show this help message and exit

Arguments:\n
    <target_app>            Path to the target Windows application\n
    <encryption_algorithm>  Encryption algorithm (AES, ChaCha20, or Twofish)\n
    <size_manipulation>     File size manipulation in MB\n
    <custom_variable>       Custom variable X\n
    <duration>              Encryption duration in minutes\n

Example:
encrypt-o-matic.exe C:\\path\\to\\app.exe AES 10 0-100000 60

This will encrypt 'app.exe' using AES, increase its size by 10MB,
perform a custom operation incrementing from 0 to 100000,
and keep it encrypted for 60 minutes.

After running the command, you will be prompted to enter a master password.
"""
)
@click.argument('target_app', 
                type=click.Path(exists=True, readable=True, file_okay=True, dir_okay=True),
                required=True)

@click.argument('encryption_algorithm', 
                type=click.Choice(["AES", "ChaCha20", "TwoFish"], case_sensitive=False),
                required=True)

@click.argument('size_manipulation', 
                type=click.IntRange(1,1000),
                required=True)

@click.argument('custom_variable', 
                type=str,
                required=True)

@click.argument('duration', 
                type=click.IntRange(1,10000),
                required=True)

def cli(target_app, encryption_algorithm, size_manipulation, custom_variable, duration):
    key = getpass.getpass("Enter a master password: ")

    if '-' not in custom_variable:
        print("Invalid custom variable")
        return
    parts = custom_variable.split('-')
    if not parts[0].isdigit() or not parts[1].isdigit():
        print("Custom variable start and end must be integers")
        return
    
    start, end = int(parts[0]), int(parts[1])
    if start >= end:
        print("Custom variable start must be less than end")
        return
    if end > 10_000_000:
        print("Custom variable end must be less than 10,000,000")
        return

    click.echo(f"Target app: {target_app}")
    click.echo(f"Algorithm: {encryption_algorithm}")
    click.echo(f"Size manipulation: {size_manipulation} MB")
    click.echo(f"Custom variable: {custom_variable}")
    click.echo(f"Duration: {duration} minutes")

    match encryption_algorithm:
        case "AES":
            encrypt_file_AES(key, target_app, size_manipulation, duration, custom_variable)
        case "ChaCha20":
            encrypt_file_ChaCha20(key, target_app, size_manipulation, duration, custom_variable)
        case "TwoFish":
            encrypt_file_TwoFish(key, target_app, size_manipulation, duration, custom_variable)
    print("\n")
    
if __name__ == "__main__":
    cli()