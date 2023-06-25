import discord
import random
import string
import smtplib
import email.message
import asyncio
import csv
server_id=1121906304101916822
chaves = {}
intents = discord.Intents.default() 
client = discord.Client(intents=intents)
def enviar_email(codigo, email_address, user_id):
    corpo_email = f"Seu código de verificação: {codigo}"

    msg = email.message.Message()
    msg['Subject'] = "Código de Verificação"
    msg['From'] = 'botcinnamonrroll@gmail.com'  
    msg['To'] = email_address
    password = 'izighgirttrznexk'  
    msg.set_payload(corpo_email)

    s = smtplib.SMTP('smtp.gmail.com: 587')
    s.starttls()
    s.login(msg['From'], password)
    s.sendmail(msg['From'], [msg['To']], msg.as_string().encode('utf-8'))
    print('E-mail enviado')


    chaves[codigo] = user_id

intents = discord.Intents.default()
intents.members = True

bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} está funcionando')

@bot.event
async def on_member_join(member):
    mensagem = f"Bem-vindo ao servidor! Por favor, verifique seu e-mail para prosseguir.\n\n" \
               f"Para verificar seu e-mail, envie o comando `!verificar_email` seguido do seu e-mail." \
               f"Exemplo: `!verificar_email seu_email@example.com`"
    await member.send(mensagem)
    guild = member.guild
    cargo_desejado = discord.utils.get(guild.roles, name='pretendente')
    if cargo_desejado is not None:
        await member.add_roles(cargo_desejado)
        print(f'Cargo {cargo_desejado.name} adicionado a {member.display_name}')
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith('!verificar_email'):
        email_address = message.content.split(' ')[1]
        codigo = gerar_codigo()
        user_id = message.author.id
        enviar_email(codigo, email_address, user_id)

        await message.author.send('Código de verificação enviado para o e-mail.')
        await aguardar_verificacao(user_id, message.author, email_address)

async def aguardar_verificacao(user_id, author, email_address):
    def check(m):
        return m.author.id == user_id and m.content.isdigit() and m.channel.type == discord.ChannelType.private

    try:
        message = await bot.wait_for('message', check=check, timeout=300)
        codigo = message.content
        if codigo in chaves and chaves[codigo] == user_id:
            del chaves[codigo]
            await author.send('Código válido! Você foi verificado.')
            guild = bot.get_guild(server_id)
            arquivo_encontrado = verificar_email(email_address)
            if arquivo_encontrado == "alunos.csv":
                role_name = "aluno"
            elif arquivo_encontrado == "professores.csv":
                role_name = "professor"
            else:
                await author.send('O email não foi encontrado no nosso banco de dados, você será banido do servidor')
                guild = bot.get_guild(server_id)
                member = guild.get_member(user_id)
                await member.ban(reason='email não encontrado.')
                return
            member = guild.get_member(user_id)
            cargo_desejado = discord.utils.get(guild.roles, name=role_name)
            if cargo_desejado is not None:
                await member.add_roles(cargo_desejado)
                print(f'Cargo {cargo_desejado.name} adicionado a {member.display_name}')
                cargo_a_remover = discord.utils.get(guild.roles, name='pretendente') 
                await member.remove_roles(cargo_a_remover)
        else:
            await author.send('Código inválido! Tente novamente ou entre em contato com o suporte.')
    except asyncio.TimeoutError:
        await author.send('Tempo limite para enviar o código expirado. Você será banido do servidor.')
        guild = bot.get_guild(server_id)
        member = guild.get_member(user_id)
        await member.ban(reason='Tempo limite para verificação expirado.')
def gerar_codigo():
    codigo = ''.join(random.choices(string.digits, k=6))
    return codigo

def verificar_email(email):
    arquivos_csv = ['alunos.csv', 'professores.csv']

    for arquivo in arquivos_csv:
        with open(arquivo, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                if email in row:
                    return arquivo

    return None
bot.run('MTEyMTkwODUyOTY0MTU2MjE3Mg.GZnlgF.jpOcLVpljByONtEicaWUNm1XKCs-7yMup9PGN8')
