/** Dicionário de referência: as chaves daqui tipam todos os outros locales. */

const ptBR = {
  meta: {
    title: "Tangerine Talk — tutor de idiomas com IA",
    description:
      "Fale, ouça, escreva e teste até alcançar a fluência, com um tutor de IA que dá feedback instantâneo.",
  },
  common: {
    loading: "Carregando…",
    back: "Voltar",
    next: "Continuar",
    cancel: "Cancelar",
    save: "Salvar",
    genericError: "Algo deu errado. Tente de novo.",
    interfaceLanguage: "Idioma da aplicação",
  },
  login: {
    title: "Bem-vindo de volta",
    subtitle: "Entre com sua conta para continuar estudando.",
    email: "E-mail",
    password: "Senha",
    submit: "Entrar",
    submitting: "Entrando…",
    invalid: "E-mail ou senha inválidos.",
    restricted: "Esta instância é por convite. Peça um link ao owner.",
  },
  invite: {
    title: "Você foi convidado",
    invitedFor: "Convite para",
    expires: "Expira em",
    name: "Seu nome",
    password: "Crie uma senha",
    passwordHint: "Use ao menos 12 caracteres.",
    submit: "Criar minha conta",
    submitting: "Criando…",
    invalid: "Este convite é inválido ou já expirou.",
    used: "Este convite já foi usado.",
  },
  onboarding: {
    title: "Vamos configurar seu estudo",
    subtitle: "Três escolhas rápidas e você já pode começar.",
    step: "Etapa {current} de {total}",
    interfaceTitle: "Em que idioma você quer usar o app?",
    interfaceHelp: "Define textos, instruções, glossas e feedback.",
    otherLocale: "Outro código de idioma",
    otherLocaleHelp: "Ex.: es-ES, fr-FR, zh-Hans-CN",
    targetTitle: "Qual idioma você quer estudar?",
    targetHelp: "Qualquer um. O app não limita a lista de idiomas-alvo.",
    targetLabel: "Código do idioma estudado",
    targetHelpCode: "Use um código como ja-JP, de-DE ou ko-KR.",
    levelTitle: "Qual é o seu nível?",
    goalTitle: "Meta diária",
    goalHelp: "Minutos por dia",
    modeTitle: "Como serão seus exercícios",
    modeBilingual: "Traduções entre o idioma da aplicação e o idioma estudado.",
    modeMonolingual:
      "Mesmo idioma nos dois lados: sem tradução, foco em leitura, gramática e pronúncia.",
    finish: "Começar a estudar",
    saving: "Salvando…",
    required: "Escolha uma opção para continuar.",
    targetRequired: "Informe o código do idioma que quer estudar.",
    invalidLocale: "Código inválido. Tente algo como pt-BR ou ja-JP.",
  },
  app: {
    title: "Seu espaço",
    subtitle: "Sua conta, suas preferências e seu progresso — isolados dos demais.",
    profile: "Seu perfil",
    interfaceLanguage: "Idioma da aplicação",
    targetLanguage: "Idioma estudado",
    notSet: "Não definido",
    mode: "Modo dos exercícios",
    level: "Nível",
    dailyGoal: "Meta diária",
    minutes: "minutos",
    bilingual: "Bilíngue",
    monolingual: "Monolingual",
    logout: "Sair",
    comingSoon: "O motor de lições está sendo construído. Volte em breve.",
    completeOnboarding: "Concluir configuração",
  },
  locale: {
    label: "Idioma",
    "pt-BR": "Português (Brasil)",
    "en-US": "English (United States)",
  },
} as const;

type MutableStrings<T> = {
  -readonly [K in keyof T]: T[K] extends string ? string : MutableStrings<T[K]>;
};

export type Dictionary = MutableStrings<typeof ptBR>;

const dictionary: Dictionary = ptBR;
export default dictionary;
