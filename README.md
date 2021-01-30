# HIGHSKYBOT
Un bot discord Français destiné à modérer le serveur discord HIGHSKY.

# Comment faire fonctionner le bot ?

Pour faire fonctionner le bot, vous devez dans un premier lieu cloner le repo, puis créer une application sur le site Discord developers, afin de récupérer un token. Pour ce faire, vous pouvez suivre ce lien : https://dev.to/quentinium/creer-son-propre-bot-discord-pio .

Attention toutefois, il est important de cocher les cases "member intents" et "presence intents" si vous voulez faire fonctionner le bot.

Il va ensuite falloir créer un fichier nommé `config.json` à la racine de votre fichier, dans lequel vous allez rentrer les informations suivantes: 

```json
{
	"prefix":"?",
	"description":"HIGHSKY BOT made by HerbeMalveillante",
	"token":"<token de votre bot>",
	"color":"3319890",
	"timeout":"60.0",
	"admins":["<Identifiant de l'admin 1>", "<Identifiant de l'admin 2>"],
	"ticketChannels":["<identifiant du salon de tickets 1>", "<identifiant du salon de tickets 2>"],
	"badWords":["<mot interdit 1>", "<mot iterdit 2>"],
	"roleMute":"<id du role à donner aux utilisateurs mutés>",
	"ticketCategory":"<id de la catégorie dans laquelle créer les salons de tickets>",
	"defaultRole":"<id du rôle par défaut>"
}
```

Note : la plupart des identifiants sont obtenables avec clic droit -> copier l'identifiant sur discord (les options développeur doivent être activées).
Les paramètres sous forme de liste peuvent contenir autant d'éléments que désiré, séparés par une virgule.

# Comment remettre à zéro la liste des warns ?

Il suffit de remettre le fichier `warns.json` dans son état initial, c'est à dire : 

```json
{}
```
