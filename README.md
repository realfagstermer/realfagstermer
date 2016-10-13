Realfagstermers prosjektrom
==============

Dette er et åpent prosjektrom for [Realfagstermer](http://www.ub.uio.no/om/tjenester/emneord/realfagstermer.html). Her tester vi *issue trackeren* til GitHub som saksbehandlingssystem for å diskutere og behandle nye termer og endringer.

* [**→ Til termdiskusjonene**](https://github.com/realfagstermer/realfagstermer/issues)

Tips:
- Du [blir varslet](https://help.github.com/articles/about-notifications/) hver gang noen [nevner deg](https://github.com/blog/821). Du blir også varslet når det kommer nye innlegg i diskusjoner du har opprettet eller kommentert. Som standard får du varslinger på epost, men du kan endre dette [i innstillingene dine](https://github.com/settings/notifications).
 - Hvis du ønsker tilbakemeldinger fra bestemte personer, f.eks. fagreferenter i de-og-de fagene, er det lurt å [nevne dem](https://github.com/blog/821). Under finnes det en oversikt over hvem-er-hvem.
- [Watch](https://help.github.com/articles/watching-repositories/ Watching repositories) : innebærer at du får en enorm mengde varsler om absolutt alle oppdateringer i alle saker. Det ønsker du mest sannsynlig ikke :)
- Alle diskusjoner foregår i det samme rommet, men vi bruker etiketter (*labels*) for å organisering. Se [dette dokumentet](https://github.com/realfagstermer/realfagstermer/blob/master/CONTRIBUTING.md) for mer info.

[![Throughput Graph](https://graphs.waffle.io/realfagstermer/realfagstermer/throughput.svg)](https://waffle.io/realfagstermer/realfagstermer/metrics)

## Deltakere:

Universitetsbiblioteket i Oslo, sortert alfabetisk etter brukernavn:

* [@bibliomari](https://github.com/bibliomari) :
  Mari Lundevall, bibliotekar.
* [@BioHeidi](https://github.com/BioHeidi) :
  Heidi Konestabo, fagansvar for biovitenskap.
* [@danmichaelo](https://github.com/danmichaelo) :
  Dan Michael O. Heggø, fagansvar for fysikk og materialvitenskap, utvikler av Okapi.
* [@grosyn](https://github.com/grosyn) :
  Gro Synnøve Nesland Lindgaard, bibliotekar, UBO/Naturhistorisk museum.
* [@knuthe](https://github.com/knuthe) :
  Knut Hegna, fagansvar for informatikk, utvikler av Roald og Sonja.
* [@kristinran](https://github.com/kristinran) :
  Kristin Rangnes, fagansvar for geofag.
* [@kyrretl](https://github.com/kyrretl) :
  Kyrre Traavik Låberg, fagansvar for biovitenskap, utvikler av emnesøket.
* [@superLine](https://github.com/superLine) :
  Line Nybakk Akerholt, bibliotekar, fagansvar forastrofysikk.
* [@TorgunnKarolineMoe](https://github.com/TorgunnKarolineMoe) :
  Karoline Moe, fagansvar for matematikk.
* [@violabibaluba](https://github.com/violabibaluba) :
  Viola Kuldvere, **redaksjonsleder** og bibliotekar.
* Tone Charlotte Gadmar, fagansvar for kjemi.
* Bente Kathrine Rasch, bibliotekar, fagansvar for farmasi.

Universitetsbiblioteket i Bergen, sortert alfabetisk etter brukernavn:
* [@bubir](https://github.com/bubir) :
  Ingunn Rødland, fagansvar for kjemi.
* [@Hypsibius](https://github.com/Hypsibius) :
  Hege Folkestad, fagansvar for biovitenskap.
* [@jw-geo](https://github.com/jw-geo) :
  Johannes Wiest, student som jobber med klass av geologi.
* [@mittinatten](https://github.com/mittinatten) :
  Simon Mitternacht, fagansvar for matematikk, informatikk og fysikk (teoretisk).
* [@mzyg](https://github.com/mzyg) :
  Marta Zygmuntowska, fagansvar for geofag, fysikk (anvendt) og teknologi.

For å varsle alle: @realfagstermer/alle

## Prosjekt «Realfagstermar på nynorsk»

Deltakarar:
* [@mariaksv](https://github.com/mariaksv) : Maria Svendsen (biologi/kjemi)
* [@jorgenem](https://github.com/jorgenem) : Jørgen Eriksson Midtbø (fysikk/matte)
* [@totlevase](https://github.com/totlevase) : Vebjørn Sture (korrektur/nynorsk)

Sjå [retningslinjer/diskusjon](https://github.com/realfagstermer/realfagstermer/wiki/Retningslinjer-for-nynorskomsetjing) og [eigen prosjektside](https://github.com/realfagstermer/prosjekt-nynorsk).

## Eksterne ressurser

* [Emnesøk](http://app.uio.no/ub/emnesok/?id=UREAL)
* [LodLive](http://biblionaut.net/lodlive)


## Conversion

Authority data is currently maintained in Sonja and converted to
JSON (RoaldIII data model) using [RoaldIII](https://github.com/realfagstermer/roald).
RoaldIII is also used to mix in mappings and translations before exporting
RDF/SKOS and MARC21.

The conversion is done by running `python publish.py`, which only
runs a conversion if any of the source files have changed. You
can run `python publish.py -f` to force a conversion even if no
source files have changed (useful during development).

Please see the RoaldIII repo for more details on the conversion.

The RoaldIII JSON data is found in `realfagstermer.json`. This does
not currently include data from the Nynorsk translation project.
Complete, distributable RDF/SKOS and MARC21 files are found in the
`dist` folder. These includes mappings and all translations.

## Data model

Example concept in JSON:

```json
{
  "id": "REAL004162",
  "type": [
    "Topic"
  ],
  "created": "2014-08-25T00:00:00Z",
  "modified": "2014-12-17T00:00:00Z",
  "prefLabel": {
    "nb": {
      "value": "Cellekommunikasjon"
    },
    "en": {
      "value": "Cell signalling"
    }
  },
  "altLabel": {
    "nb": [
      {
        "value": "Cellesignalisering"
      }
    ],
    "en": [
      {
        "value": "Cell signaling"
      }
    ]
  },
  "hiddenLabel": {}
},
```

Characteristics:

* Realfagstermer contains only concepts, no facets, arrays or other thesaurus constructs.
* Concept properties
  * `id` (string): an unique identifier.
  * `type` (array): at least one type (`Topic`, `Geographic`, `Temporal`, `GenreForm`, `CompoundHeading` or `VirtualCompoundHeading`).
  * `created` (datetime string): a creation date.
  * `modified` (datetime string): a modification date.
  * `prefLabel` (language map): one preferred term per language. A preferred term for the language code `nb` is required, while others are optional.
  * `altLabel` (language map array): any number of alternative terms per language.
  * `hiddenLabel` (langauge map array): any number of hidden terms (not yet implemented).
  * `editorialNote` (array): any number of editorial notes (in Bokmål only).
  * `definition` (language map): one definition per language (currently only Bokmål though).
  * `ddc` (string): a DDC number (these should eventually be moved to the mapping project).
  * `msc` (string): a MSC number.
  * `elementSymbol` (string): a chemical element symbol.
  * `related` (array): Any number of IDs for related concepts.
  * `broader` (array): Any number of IDs for broader concepts.
  * `narrower` (array): Any number of IDs for narrower concepts.
  * `component` (array): Any number of IDs for components that make up the
    `CompoundHeading` or `VirtualCompoundHeading` (*emnestreng*). Note that concepts of
    this type do not have their own terms, since the compound terms are generated from the concepts.
    Example:

    ```json
    {
      "id": "REAL014060",
      "type": [
        "CompoundHeading"
      ],
      "created": "2015-03-10T10:07:34Z",
      "component": [
        "REAL002845",
        "REAL007608"
      ]
    }
    ```

* Term properties:
  * `value` (string): The term value.
  * `hasAcronym` (string): An acronym (used only if `value` is the full form).
  * `acronymFor` (string): The full form (used only if `value` is an acronym).
* Note that terms do not have their own IDs, so the relationship between acronyms and their
  full form is represented by embedding. Example:

  ```json
  {
    "prefLabel": {
      "nb": {
        "hasAcronym": "DCOM",
        "value": "Distributed component object model"
      }
    }
  }
  ```

  When converting to SKOS core, we simplify the model by removing term-term relationships.
