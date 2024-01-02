import threading
import json
import random
import discord
from discord.ext import commands

class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None

    def add_command(self, command):
        new_node = Node(command)
        new_node.next = self.head
        self.head = new_node

class CommandHistory:
    def __init__(self):
        self.history = {}
        self.lock = threading.Lock()

    def add_user_command(self, user_id, command):
        with self.lock:
            if user_id not in self.history:
                self.history[user_id] = LinkedList()
            self.history[user_id].add_command(command)

    def get_last_command(self, user_id):
        if user_id in self.history and self.history[user_id].head:
            return self.history[user_id].head.data
        return None

    def get_all_commands(self, user_id):
        if user_id in self.history:
            current = self.history[user_id].head
            while current:
                print(current.data)
                current = current.next

    def clear_history(self, user_id):
        if user_id in self.history:
            self.history[user_id] = LinkedList()

class QuestionNode:
    def __init__(self, question, yes=None, no=None):
        self.question = question
        self.yes = yes
        self.no = no

class ConversationTree:
    def __init__(self):
        self.root = QuestionNode("Y a-t-il quelque chose de spécifique que vous aimeriez savoir ?")

    def start_conversation(self):
        return self.root

class ConversationManager:
    def __init__(self):
        self.tree = ConversationTree()
        self.current_node = self.tree.start_conversation()

    def reset_conversation(self):
        self.current_node = self.tree.start_conversation()

    def speak_about(self, topic):
        if topic.lower() == 'reset':
            self.reset_conversation()
            return "Réinitialisation de la conversation. Demandez-moi n’importe quoi !"
        else:
            return f"Je peux {'' if self.find_topic(self.current_node, topic.lower()) else 'not '}parler de {topic}."

    def find_topic(self, node, topic):
        if node is None:
            return False
        if node.question.lower() == topic:
            return True
        return self.find_topic(node.yes, topic) or self.find_topic(node.no, topic)

class UserDataTable:
    def __init__(self):
        self.user_data = {}

    def add_user_data(self, user_id, data):
        self.user_data[user_id] = data

    def get_user_data(self, user_id):
        return self.user_data.get(user_id, None)

class DataSaver:
    @staticmethod
    def save_data(filename, data):
        with open(filename, 'w') as file:
            json.dump(data, file)

    @staticmethod
    def load_data(filename):
        try:
            with open(filename, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

bot = commands.Bot(command_prefix='!')
history_manager = CommandHistory()
conversation_manager = ConversationManager()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('------')

@bot.command(name='lastcommand') #Affiche la dernière commande de l'utilisateur
async def last_command(ctx):
    user_id = str(ctx.author.id)
    last_command = history_manager.get_last_command(user_id)
    if last_command:
        await ctx.send(f"Last command: {last_command}")
    else:
        await ctx.send("Pas d'historique de commandes.")

@bot.command(name='allcommands') #Affiche toutes les commandes de l'utilisateur
async def all_commands(ctx):
    user_id = str(ctx.author.id)
    await ctx.send(f"All commands for user {user_id}:")
    history_manager.get_all_commands(user_id)

@bot.command(name='clearhistory')#Efface l'historique des commandes de l'utilisateur
async def clear_history(ctx):
    user_id = str(ctx.author.id)
    history_manager.clear_history(user_id)
    await ctx.send("Historique des commandes effacé.")

@bot.command(name='startconversation')#Démarre une nouvelle conversation
async def start_conversation(ctx):
    user_id = str(ctx.author.id)
    conversation_manager.reset_conversation()
    await ctx.send("onversation réinitialisée. Posez-moi n'importe quelle question !")

@bot.command(name='speakabout')#Vérifie si le bot peut parler d'un certain sujet dans le contexte de la conversation
async def speak_about(ctx, topic):
    response = conversation_manager.speak_about(topic)
    await ctx.send(response)

@bot.command(name='guessnumber')
async def guess_number(ctx, number: int):
    """Jeu de devinette de nombre."""
    guessed_number = random.randint(1, 10)
    if number == guessed_number:
        await ctx.send(f'Bravo ! Tu as deviné le bon nombre ({guessed_number}).')
    else:
        await ctx.send(f'Désolé, le bon nombre était {guessed_number}. Essaie à nouveau !')

@bot.command(name='randomquote')
async def random_quote(ctx):
    """Renvoie une citation aléatoire."""
    quotes = ["La vie est courte, l'art est long. - Hippocrate",
              "Le succès, c'est d'aller d'échec en échec sans perdre son enthousiasme. - Winston Churchill",
              "La créativité, c'est l'intelligence qui s'amuse. - Albert Einstein"]
    random_quote = random.choice(quotes)
    await ctx.send(random_quote)

@bot.command(name='dice')
async def roll_dice(ctx, sides: int = 6):
    """Lance un dé avec le nombre de côtés spécifié (par défaut : 6 côtés)."""
    result = random.randint(1, sides)
    await ctx.send(f'Tu as lancé un dé de {sides} côtés et obtenu le résultat : {result}')

@bot.command(name='randomresponse')
async def random_response(ctx):
    """Renvoie une réponse aléatoire amusante."""
    responses = ["Bien sûr !",
                 "Non, désolé.",
                 "Peut-être plus tard.",
                 "Je ne suis pas sûr de comprendre la question."]
    random_response = random.choice(responses)
    await ctx.send(random_response)

@bot.command(name='randomjoke')
async def random_joke(ctx):
    """Renvoie une blague aléatoire."""
    jokes = ["Pourquoi les plongeurs plongent-ils toujours en arrière et jamais en avant ? Parce que sinon ils tombent toujours dans le bateau.",
             "Qu'est-ce qu'un crocodile avec une machine ? Un crocodile-dentiste !",
             "Pourquoi les plongeurs plongent-ils toujours en arrière et jamais en avant ? Parce que sinon ils tombent toujours dans le bateau."]
    random_joke = random.choice(jokes)
    await ctx.send(random_joke)

@bot.command(name='randomfact')
async def random_fact(ctx):
    """Renvoie un fait intéressant aléatoire."""
    facts = ["Les abeilles peuvent reconnaître les visages humains.",
             "Les éléphants sont les seuls animaux qui ne peuvent pas sauter.",
             "Un nuage moyen pèse autant que 100 éléphants."]
    random_fact = random.choice(facts)
    await ctx.send(random_fact)

bot.run('MTE2NzM5ODY0NzgyNzI4NDA3OQ.G27ZFi.QppK8iaQYylYSck8K_3YqVD_LK_595nmox1Qdc')
