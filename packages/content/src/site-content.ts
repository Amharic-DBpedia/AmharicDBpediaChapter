import type {
  ChapterMetric,
  Contributor,
  DatasetArtifact,
  MappingStatistic,
  NavItem,
  NewsItem,
  QueryExample,
  ResearchHighlight,
  ResourceLink,
  TeamMember,
} from "./types";

export const languages = {
  en: "English",
  am: "አማርኛ",
  de: "Deutsch",
} as const;

export const navigation: readonly NavItem[] = [
  { href: "/", label: { en: "Home", am: "መነሻ", de: "Start" } },
  { href: "/news", label: { en: "News", am: "ዜና", de: "Aktuelles" } },
  { href: "/statistics", label: { en: "Statistics", am: "ስታቲስቲክስ", de: "Statistik" } },
  { href: "/datasets", label: { en: "Datasets", am: "ዳታሴቶች", de: "Datensätze" } },
  { href: "/sparql", label: { en: "SPARQL", am: "SPARQL", de: "SPARQL" } },
  { href: "/resource/ደብረ_ብርሃን", label: { en: "Resource", am: "ምንጭ", de: "Ressource" } },
  { href: "/team", label: { en: "Team", am: "ቡድን", de: "Team" } },
  { href: "/docs", label: { en: "Docs", am: "ሰነዶች", de: "Dokumente" } },
];

export const chapterMetrics: readonly ChapterMetric[] = [
  {
    label: { en: "Mapped templates", am: "የተዛመዱ መለጠፊያዎች", de: "Gemappte Vorlagen" },
    value: "97",
    tone: "primary",
    detail: {
      en: "GSoC 2025 report: 100% template coverage after mapping cleanup.",
      am: "የGSoC 2025 ሪፖርት፡ ከማጽዳት በኋላ 100% የመለጠፊያ ሽፋን።",
      de: "GSoC-2025-Bericht: 100% Vorlagenabdeckung nach Mapping-Bereinigung.",
    },
  },
  {
    label: { en: "Property coverage", am: "የባህሪ ሽፋን", de: "Property-Abdeckung" },
    value: "77.29%",
    tone: "accent",
    detail: {
      en: "Improved from 15.70% after template alignment and ontology corrections.",
      am: "ከመለጠፊያ ማስተካከያ እና ኦንቶሎጂ ማረሚያ በኋላ ከ15.70% ተሻሽሏል።",
      de: "Verbessert von 15,70% durch Vorlagenabgleich und Ontologie-Korrekturen.",
    },
  },
  {
    label: { en: "Property occurrences", am: "የባህሪ ክስተቶች", de: "Property-Vorkommen" },
    value: "99.15%",
    tone: "warm",
    detail: {
      en: "Coverage reported after switching statistics to infobox-properties.ttl.",
      am: "ስታቲስቲክስ ወደ infobox-properties.ttl ከተቀየረ በኋላ የተመዘገበ ሽፋን።",
      de: "Abdeckung nach Umstellung der Statistik auf infobox-properties.ttl.",
    },
  },
  {
    label: { en: "Unique triples", am: "ልዩ RDF ትሪፕሎች", de: "Eindeutige Tripel" },
    value: "528,370",
    tone: "primary",
    detail: {
      en: "Research paper release count for the extracted Amharic DBpedia knowledge graph.",
      am: "በምርምር ጽሑፉ የተመዘገበ የአማርኛ DBpedia የተወጣ የእውቀት ግራፍ መጠን።",
      de: "Im Forschungspapier berichtete Anzahl extrahierter Amharic-DBpedia-Tripel.",
    },
  },
];

export const mappingStatistics: readonly MappingStatistic[] = [
  {
    label: "Templates mapped",
    percentage: "100.00%",
    count: "84 / 84",
    description: "Distinct Amharic infobox templates linked to DBpedia mappings.",
  },
  {
    label: "Properties mapped",
    percentage: "77.29%",
    count: "2,392 / 3,095",
    description: "Template parameters assigned to DBpedia ontology properties.",
  },
  {
    label: "Template occurrences mapped",
    percentage: "100.00%",
    count: "3,958 / 3,958",
    description: "Total uses of mapped templates across Amharic Wikipedia pages.",
  },
  {
    label: "Property occurrences mapped",
    percentage: "99.15%",
    count: "19,799 / 19,968",
    description: "Total occurrences of mapped properties in Amharic Wikipedia.",
  },
];

export const researchHighlights: readonly ResearchHighlight[] = [
  {
    title: {
      en: "Amharic-aware extraction",
      am: "አማርኛን የሚያውቅ extraction",
      de: "Amharic-bewusste Extraktion",
    },
    body: {
      en: "The paper extends DEF with Ethiopian date parsing, Ethiopian-Gregorian calendar conversion, and Arabic-Ge'ez numeral conversion.",
      am: "ጽሑፉ DEFን በኢትዮጵያ ቀን 解析፣ የኢትዮጵያ-ጎርጎርዮሳዊ ቀን መቀየሪያ፣ እና የአረብኛ-Ge'ez ቁጥር መቀየሪያ ያሰፋዋል።",
      de: "Das Paper erweitert DEF um äthiopische Datumsparser, Kalenderkonvertierung und Arabic-Ge'ez-Zahlenkonvertierung.",
    },
  },
  {
    title: {
      en: "Translation-assisted mappings",
      am: "በትርጉም የታገዘ mapping",
      de: "Übersetzungsgestützte Mappings",
    },
    body: {
      en: "Zero-shot NLLB-200 reached BLEU 45.31 on Amharic infobox property translation, useful as a draft generator but still requiring review.",
      am: "Zero-shot NLLB-200 በአማርኛ infobox property ትርጉም BLEU 45.31 አግኝቷል፤ ለመነሻ ይጠቅማል ግን ሰው ማረጋገጥ ይፈልጋል።",
      de: "Zero-shot NLLB-200 erreichte BLEU 45,31 und eignet sich als Entwurfshilfe, braucht aber Review.",
    },
  },
  {
    title: { en: "Ontology alignment", am: "Ontology alignment", de: "Ontologie-Abgleich" },
    body: {
      en: "Fine-tuned Afro-XLM-R reached 92.1% Top-10 accuracy and 78.8 MRR for class-aware ontology property alignment.",
      am: "Fine-tuned Afro-XLM-R በclass-aware ontology property alignment 92.1% Top-10 accuracy እና 78.8 MRR አግኝቷል።",
      de: "Fine-tuned Afro-XLM-R erreichte 92,1% Top-10 Accuracy und 78,8 MRR.",
    },
  },
];

export const newsItems: readonly NewsItem[] = [
  {
    title: {
      en: "A knowledge graph for Amharic presented at LREC 2026",
      am: "የአማርኛ የእውቀት ግራፍ በLREC 2026 ቀርቧል",
      de: "Ein Wissensgraph fuer Amharisch auf der LREC 2026 vorgestellt",
    },
    summary: {
      en: 'Hizkiel Mitiku Alemayehu presented "The Amharic DBpedia Chapter: A Knowledge Graph for a Low-Resource Language" at the 15th Language Resources and Evaluation Conference in Palma de Mallorca.',
      am: 'ሕዝቅኤል ምትኩ አለማየሁ "The Amharic DBpedia Chapter" የተሰኘውን ጽሑፍ በPalma de Mallorca በተካሄደው 15ኛው LREC አቅርቧል።',
      de: 'Hizkiel Mitiku Alemayehu stellte "The Amharic DBpedia Chapter" auf der 15. Language Resources and Evaluation Conference in Palma de Mallorca vor.',
    },
    category: { en: "Research", am: "ምርምር", de: "Forschung" },
    publishedAt: "2026-05-15",
    href: "https://lrec.elra.info/lrec2026-main-627",
    actionLabel: {
      en: "Read the paper",
      am: "ጽሑፉን ያንብቡ",
      de: "Paper lesen",
    },
    links: [
      {
        label: { en: "LREC paper page", am: "የLREC ጽሑፍ ገጽ", de: "LREC-Paperseite" },
        href: "https://lrec.elra.info/lrec2026-main-627",
      },
      {
        label: { en: "GitHub resources", am: "የGitHub ምንጮች", de: "GitHub-Ressourcen" },
        href: "https://github.com/Amharic-DBpedia/",
      },
    ],
  },
  {
    title: {
      en: "Open Amharic DBpedia resources released for reuse",
      am: "ክፍት የአማርኛ DBpedia ምንጮች ለዳግም አጠቃቀም ተለቀቁ",
      de: "Offene Amharic-DBpedia-Ressourcen zur Wiederverwendung veroeffentlicht",
    },
    summary: {
      en: "The project publishes the Amharic knowledge graph, extraction assets, chapter resources, public Databus artifacts, and a Tentris query endpoint for exploration.",
      am: "ፕሮጀክቱ የአማርኛ የእውቀት ግራፍን፣ extraction assets፣ chapter resources፣ Databus artifacts እና Tentris query endpoint ያቀርባል።",
      de: "Das Projekt veroeffentlicht den Amharic-Wissensgraphen, Extraktionsressourcen, Databus-Artefakte und einen Tentris-Abfrageendpunkt.",
    },
    category: { en: "Resources", am: "ምንጮች", de: "Ressourcen" },
    publishedAt: "2026-05-15",
    href: "/sparql",
    actionLabel: {
      en: "Explore the graph",
      am: "ግራፉን ይመልከቱ",
      de: "Graph erkunden",
    },
    links: [
      {
        label: {
          en: "Amharic DBpedia GitHub",
          am: "Amharic DBpedia GitHub",
          de: "Amharic-DBpedia-GitHub",
        },
        href: "https://github.com/Amharic-DBpedia/",
      },
      {
        label: {
          en: "Tentris query endpoint",
          am: "Tentris query endpoint",
          de: "Tentris-Abfrageendpunkt",
        },
        href: "https://am.dbpedia.data.dice-research.org/ui",
      },
      {
        label: { en: "Databus collection", am: "Databus collection", de: "Databus-Collection" },
        href: "https://databus.dbpedia.org/purplebee/collections/am_chapter/",
      },
    ],
  },
  {
    title: {
      en: "GSoC extraction release reaches 528,370 unique triples",
      am: "የGSoC extraction release 528,370 ልዩ triples ደርሷል",
      de: "GSoC-Extraktionsrelease erreicht 528.370 eindeutige Tripel",
    },
    summary: {
      en: "The latest chapter release documents complete template mapping coverage and a major increase in mapped property occurrences.",
      am: "የቅርብ ጊዜው chapter release ሙሉ የtemplate mapping ሽፋንን እና በmapped property occurrences ላይ ከፍተኛ ጭማሪን ያሳያል።",
      de: "Das aktuelle Chapter-Release dokumentiert vollstaendige Template-Abdeckung und einen deutlichen Anstieg gemappter Property-Vorkommen.",
    },
    category: { en: "Release", am: "ሪሊዝ", de: "Release" },
    publishedAt: "2025-08-20",
    href: "/statistics",
    actionLabel: {
      en: "View statistics",
      am: "ስታቲስቲክስ ይመልከቱ",
      de: "Statistik ansehen",
    },
    links: [
      {
        label: { en: "Statistics dashboard", am: "የስታቲስቲክስ ገጽ", de: "Statistik-Dashboard" },
        href: "/statistics",
      },
      {
        label: { en: "Published datasets", am: "የታተሙ ዳታሴቶች", de: "Veroeffentlichte Datensaetze" },
        href: "/datasets",
      },
    ],
  },
];

export const resourceLinks: readonly ResourceLink[] = [
  {
    title: { en: "SPARQL endpoint", am: "SPARQL ኤንድፖይንት", de: "SPARQL-Endpunkt" },
    description: {
      en: "Run Amharic DBpedia queries through the public Tentris UI.",
      am: "የአማርኛ DBpedia ጥያቄዎችን በTentris UI ያስኬዱ።",
      de: "Amharic-DBpedia-Abfragen über die öffentliche Tentris-Oberfläche ausführen.",
    },
    href: "https://am.dbpedia.data.dice-research.org/ui",
    image: "/assets/images/tentris.png",
  },
  {
    title: { en: "Databus collection", am: "የDatabus ስብስብ", de: "Databus-Sammlung" },
    description: {
      en: "Download published Amharic RDF dumps and release artifacts.",
      am: "የታተሙ የአማርኛ RDF ዳምፖችን እና ሪሊዝ ፋይሎችን ያውርዱ።",
      de: "Veröffentlichte Amharic-RDF-Dumps und Release-Artefakte herunterladen.",
    },
    href: "https://databus.dbpedia.org/purplebee/collections/am_chapter/",
    image: "/assets/images/databus.png",
  },
  {
    title: { en: "Mappings wiki", am: "የMapping ዊኪ", de: "Mappings-Wiki" },
    description: {
      en: "Maintain Amharic template-to-ontology mappings in DBpedia.",
      am: "የአማርኛ መለጠፊያ-ወደ-ኦንቶሎጂ ማዛመዶችን ያስተካክሉ።",
      de: "Amharic-Vorlagen-zu-Ontologie-Mappings in DBpedia pflegen.",
    },
    href: "https://mappings.dbpedia.org/index.php/Mapping_am",
    image: "/assets/images/dbpedia_am_logo.png",
  },
  {
    title: { en: "Extraction Framework", am: "Extraction Framework", de: "Extraction Framework" },
    description: {
      en: "The upstream Scala framework that turns Wikipedia dumps into RDF.",
      am: "የWikipedia ዳምፖችን ወደ RDF የሚቀይረው የScala አፕስትሪም መሣሪያ።",
      de: "Das Upstream-Scala-Framework, das Wikipedia-Dumps in RDF umwandelt.",
    },
    href: "https://github.com/dbpedia/extraction-framework",
    image: "/assets/images/github-logo.png",
  },
];

export const datasetArtifacts: readonly DatasetArtifact[] = [
  {
    name: "labels",
    type: "metadata",
    description: "Readable labels for Amharic DBpedia resources.",
  },
  { name: "instance-types", type: "raw", description: "Type assertions for extracted resources." },
  {
    name: "infobox-properties",
    type: "raw",
    description: "Infobox property output used for statistics generation.",
  },
  {
    name: "mappingbased-literals",
    type: "mapping-based",
    description: "Literal values emitted from mapped infobox fields.",
  },
  {
    name: "mappingbased-objects-uncleaned",
    type: "mapping-based",
    description: "Object links emitted from mapped infobox fields before cleanup.",
  },
  {
    name: "geo-coordinates",
    type: "metadata",
    description: "Coordinates extracted from Amharic pages and infoboxes.",
  },
  {
    name: "wikipedia-links",
    type: "metadata",
    description: "Links between Amharic Wikipedia-derived resources.",
  },
  {
    name: "article-categories",
    type: "metadata",
    description: "Category membership extracted from Amharic Wikipedia.",
  },
];

export const queryExamples: readonly QueryExample[] = [
  {
    title: { en: "Sample resources", am: "የምሳሌ ምንጮች", de: "Beispielressourcen" },
    description: {
      en: "Return a small sample of subjects from the Amharic graph.",
      am: "ከአማርኛ ግራፍ ትንሽ የርዕሶች ምሳሌ ያሳያል።",
      de: "Gibt eine kleine Auswahl von Subjekten aus dem Amharic-Graphen zurück.",
    },
    query: "SELECT ?s WHERE {\n  ?s ?p ?o .\n}\nLIMIT 10",
  },
  {
    title: { en: "Amharic labels", am: "የአማርኛ መለያዎች", de: "Amharic-Labels" },
    description: {
      en: "Find resources that have Amharic rdfs:label values.",
      am: "የአማርኛ rdfs:label ያላቸውን ምንጮች ይፈልጋል።",
      de: "Findet Ressourcen mit amharischen rdfs:label-Werten.",
    },
    query:
      'PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n\nSELECT ?resource ?label WHERE {\n  ?resource rdfs:label ?label .\n  FILTER(lang(?label) = "am")\n}\nLIMIT 20',
  },
  {
    title: { en: "Debre Birhan facts", am: "የደብረ ብርሃን መረጃ", de: "Debre-Birhan-Fakten" },
    description: {
      en: "Inspect predicates and objects for a concrete Amharic resource.",
      am: "ለተወሰነ የአማርኛ ምንጭ ባህሪዎችን እና እቃዎችን ያሳያል።",
      de: "Prüft Prädikate und Objekte für eine konkrete Amharic-Ressource.",
    },
    query:
      "SELECT ?predicate ?object WHERE {\n  <http://am.dbpedia.org/resource/ደብረ_ብርሃን> ?predicate ?object .\n}\nLIMIT 100",
  },
];

export const contributors: readonly Contributor[] = [
  {
    name: "Andargachew Asfaw",
    year: "GSoC 2025",
    role: { en: "Contributor", am: "አስተዋጽዖ አበርካች", de: "Mitwirkender" },
    href: "https://github.com/contact-andy/GSoC-25_DBpedia_Amharic_Chapter",
  },
  {
    name: "Meti Bayissa",
    year: "GSoC 2024",
    role: { en: "Contributor", am: "አስተዋጽዖ አበርካች", de: "Mitwirkende" },
    href: "https://github.com/Meti-Adane/GSOC-24_DBpedia_Amharic_Chapter",
  },
];

export const teamMembers: readonly TeamMember[] = [
  {
    name: "Prof. Dr. Ricardo Usbeck",
    role: { en: "Mentor", am: "መሪ አማካሪ", de: "Mentor" },
    affiliation: "Leuphana University of Lueneburg",
    href: "https://www.linkedin.com/in/ricardo-usbeck/",
  },
  {
    name: "Meti Bayissa",
    role: {
      en: "Mentor and GSoC 2024 contributor",
      am: "መሪ አማካሪ እና GSoC 2024 አስተዋጽዖ አበርካች",
      de: "Mentorin und GSoC-2024-Mitwirkende",
    },
    affiliation: "Addis Ababa University",
    href: "https://www.linkedin.com/in/metiadanebayissa/",
  },
  {
    name: "Hizkiel Mitiku Alemayehu",
    role: {
      en: "Mentor and paper author",
      am: "መሪ አማካሪ እና የጽሑፍ ደራሲ",
      de: "Mentor und Paper-Autor",
    },
    affiliation: "Paderborn University",
    href: "https://linkedin.com/in/hizkiel-mitiku-alemayehu-97306010b",
  },
  {
    name: "Tilahun Abedissa Taffa",
    role: {
      en: "Mentor and paper author",
      am: "መሪ አማካሪ እና የጽሑፍ ደራሲ",
      de: "Mentor und Paper-Autor",
    },
    affiliation: "University of Hamburg / Leuphana University",
    href: "https://www.linkedin.com/in/tilahun-abedissa-47372a9a",
  },
  {
    name: "Andargachew Asfaw",
    role: {
      en: "GSoC 2025 contributor and paper author",
      am: "GSoC 2025 አስተዋጽዖ አበርካች እና የጽሑፍ ደራሲ",
      de: "GSoC-2025-Mitwirkender und Paper-Autor",
    },
    affiliation: "Addis Ababa University",
    href: "https://github.com/contact-andy/GSoC-25_DBpedia_Amharic_Chapter",
  },
  {
    name: "Hamada M. Zahera",
    role: { en: "Paper author", am: "የጽሑፍ ደራሲ", de: "Paper-Autor" },
    affiliation: "Paderborn University",
  },
  {
    name: "Axel-Cyrille Ngonga Ngomo",
    role: { en: "Paper author", am: "የጽሑፍ ደራሲ", de: "Paper-Autor" },
    affiliation: "Paderborn University",
  },
];
