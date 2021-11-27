import click

import mangorest.auth as auth


@click.group()
def runner():
    pass


@runner.command(help="Create a MangoREST user.")
@click.argument("username")
@click.password_option()
def createuser(username, password):
    auth.create_user_service(username, password)
    click.secho(f"MangoREST user created: {username}", fg="green")


if __name__ == "__main__":
    runner()
