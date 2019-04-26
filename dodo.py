# vi:autoindent:sw=4:ts=4:et
# encoding=utf8

import logging
import logging.config
import yaml

with open('logging.yml') as cfg:
    logging.config.dictConfig(yaml.safe_load(cfg))

logger = logging.getLogger()

from doit import get_var
from roald import Roald
from rdflib.graph import Graph, URIRef
import csv
import time
import json
import data_ub_tasks

config = {
    'dumps_dir': get_var('dumps_dir', '/opt/data.ub/www/default/dumps'),
    'dumps_dir_url': get_var('dumps_dir_url', 'http://data.ub.uio.no/dumps'),
    'graph': 'http://data.ub.uio.no/realfagstermer',
    'fuseki': 'http://localhost:3031/ds',
    'basename': 'realfagstermer',
    'git_user': 'ubo-bot',
    'git_email': 'danmichaelo+ubobot@gmail.com',
    'es_index': 'authority'
}

DOIT_CONFIG = {
    'default_tasks': [
        'fetch_core:src/sonja_todo.json',
        'git-push',
        'build-solr-json',
        'publish-dumps',
        'fuseki',
        'stats',
    ]
}


def task_fetch_core():

    yield {
        'doc': 'Fetch remote core files that have changed',
        'basename': 'fetch-core',
        'name': None
    }
    yield data_ub_tasks.git_pull_task_gen(config)
    for file in [
        {'remote': 'https://app.uio.no/ub/emnesok/data/ureal/rii/idtermer.txt',
            'local': 'src/idtermer.txt'},
        {'remote': 'https://app.uio.no/ub/emnesok/data/ureal/rii/idsteder.txt',
            'local': 'src/idsteder.txt'},
        {'remote': 'https://app.uio.no/ub/emnesok/data/ureal/rii/idformer.txt',
            'local': 'src/idformer.txt'},
        {'remote': 'https://app.uio.no/ub/emnesok/data/ureal/rii/idtider.txt',
            'local': 'src/idtider.txt'},
        {'remote': 'https://app.uio.no/ub/emnesok/data/ureal/rii/idstrenger.txt',
            'local': 'src/idstrenger.txt'},
        {'remote': 'https://raw.githubusercontent.com/scriptotek/data_ub_ontology/master/ub-onto.ttl',
            'local': 'src/ub-onto.ttl'},
        {'remote': 'https://raw.githubusercontent.com/realfagstermer/prosjekt-kinderegg/master/sonja_todo.json',
            'local': 'src/sonja_todo.json'},
        {'remote': 'https://raw.githubusercontent.com/realfagstermer/prosjekt-kinderegg/master/categories_and_mappings.ttl',
            'local': 'src/categories_and_mappings.ttl'},
    ]:
        yield data_ub_tasks.fetch_remote_gen(file['remote'], file['local'], ['fetch_core:git-pull'])

def task_fetch_extras():

    yield {
        'doc': 'Fetch remote extra files that have changed',
        'basename': 'fetch-extras',
        'name': None
    }
    for file in [
        {'remote': 'https://mapper.biblionaut.net/export/real_tekord_mappings.ttl',
            'local': 'src/real_tekord_mappings.ttl'},
        {'remote': 'https://mapper.biblionaut.net/export/real_agrovoc_mappings.ttl',
            'local': 'src/real_agrovoc_mappings.ttl'},
        {'remote': 'https://lambda.biblionaut.net/export/real_hume_mappings.ttl',
            'local': 'src/real_hume_mappings.ttl'},
        {'remote': 'https://lambda.biblionaut.net/export/ccmapper_mappings.ttl',
            'local': 'src/ccmapper_mappings.ttl'},
        {'remote': 'https://data.ub.uio.no/dumps/msc-ubo.mappings.nt',
            'local': 'src/msc-ubo.mappings.nt'},        # {'remote': 'https://rawgit.com/realfagstermer/prosjekt-kinderegg/master/categories_and_mappings.ttl',
        #     'local': 'src/categories_and_mappings.ttl'},
    ]:
        yield data_ub_tasks.fetch_remote_gen(file['remote'], file['local'], [])


def task_build_core():

    def build(task):
        logger.info('Building new core dist')
        roald = Roald()
        roald.load('src/', format='roald2', language='nb')
        roald.set_uri_format('http://data.ub.uio.no/%s/c{id}' % config['basename'], 'REAL')
        roald.save('%s.json' % config['basename'])
        logger.info('Wrote %s.json', config['basename'])

        includes = [
            '%s.scheme.ttl' % config['basename'],
            'src/ub-onto.ttl',
            # 'src/nynorsk.ttl'
        ]

        # 1) MARC21
        # marc21options = {
        #     'vocabulary_code': 'noubomn',
        #     'created_by': 'NO-TrBIB',
        #     'mappings_from': ['src/lambda.rdf']
        # }
        # roald.export('dist/%s.marc21.xml' %
        #              config['basename'], format='marc21', **marc21options)
        # logger.info('Wrote dist/%s.marc21.xml', config['basename'])

        # 2) RDF (core)
        roald.export('dist/%s.ttl' % config['basename'],
                     format='rdfskos',
                     include=includes
                     )
        logger.info('Wrote dist/%s.core.ttl', config['basename'])


    return {
        'doc': 'Build core distribution files (JSON + TTL)',
        'basename': 'build-core',
        'actions': [
            'mkdir -p dist',
            build,
        ],
        'file_dep': [
            'src/idtermer.txt',
            'src/idsteder.txt',
            'src/idformer.txt',
            'src/idtider.txt',
            'src/idstrenger.txt',
            'src/ub-onto.ttl',
            '%s.scheme.ttl' % config['basename']
        ],
        'targets': [
            '%s.json' % config['basename'],
            # 'dist/%s.marc21.xml' % config['basename'],
            'dist/%s.ttl' % config['basename'],
        ]
    }


def task_build_extras():

    def build(task):
        logger.info('Building extras')
        roald = Roald()
        roald.load('src/', format='roald2', language='nb')
        roald.set_uri_format('http://data.ub.uio.no/%s/c{id}' % config['basename'], 'REAL')

        roald.load('src/categories_and_mappings.ttl', format='skos')  # From soksed
        roald.load('src/real_hume_mappings.ttl', format='skos')  # Humord mappings from mymapper

        # 1) MARC21 with $9 fields for CCMapper
        marc21options = {
            'vocabulary_code': 'noubomn',
            'created_by': 'NO-TrBIB',
            'include_extras': True,
            'include_memberships': True,
        }
        roald.export('dist/%s.ccmapper.marc21.xml' %
                     config['basename'], format='marc21',
                     **marc21options)
        logger.info('Wrote dist/%s.ccmapper.marc21.xml', config['basename'])

        roald.load('src/real_tekord_mappings.ttl', format='skos')  # Tekord mappings
        roald.load('src/real_agrovoc_mappings.ttl', format='skos')  # Agrovoc mappings
        roald.load('src/ccmapper_mappings.ttl', format='skos')  # Mappings from CCMapper
        roald.load('src/msc-ubo.mappings.nt', format='skos')  # MSC mappings

        # 1) MARC21 for Alma and general use
        marc21options = {
            'vocabulary_code': 'noubomn',
            'created_by': 'NO-TrBIB',
            'include_extras': False,
            'include_memberships': False,
        }
        roald.export('dist/%s.marc21.xml' %
                     config['basename'], format='marc21', **marc21options)
        logger.info('Wrote dist/%s.marc21.xml', config['basename'])

        # 3) RDF (core + mappings)
        prepared = roald.prepare_export(format='rdfskos',
            include=[
                '%s.scheme.ttl' % config['basename'],
                'src/ub-onto.ttl',
                'src/categories_and_mappings.ttl',
            ],
            with_ccmapper_candidates=True,
            infer=True
        )
        prepared.write('dist/%s.complete.ttl' % config['basename'], format='turtle')
        logger.info('Wrote dist/%s.complete.ttl', config['basename'])
        prepared.write('dist/%s.complete.nt' % config['basename'], format='nt')
        logger.info('Wrote dist/%s.complete.nt', config['basename'])

    return {
        'doc': 'Build extra distribution files (RDF/SKOS with mappings + MARC21XML)',
        'basename': 'build-extras',
        'actions': [
            'mkdir -p dist',
            build,
        ],
        'file_dep': [
            'src/idtermer.txt',
            'src/idsteder.txt',
            'src/idformer.txt',
            'src/idtider.txt',
            'src/idstrenger.txt',
            'src/real_tekord_mappings.ttl',
            'src/real_agrovoc_mappings.ttl',
            'src/real_hume_mappings.ttl',
            'src/ccmapper_mappings.ttl',
            'src/categories_and_mappings.ttl',
            'src/msc-ubo.mappings.nt',
            'src/ub-onto.ttl',
            '%s.scheme.ttl' % config['basename']
        ],
        'targets': [
            'dist/%s.marc21.xml' % config['basename'],
            'dist/%s.ccmapper.marc21.xml' % config['basename'],
            'dist/%s.complete.ttl' % config['basename'],
            'dist/%s.complete.nt' % config['basename'],
        ]
    }

def task_build_mappings():
    src_uri = 'http://data.ub.uio.no/realfagstermer/'
    mapping_sets = [
        {
            'source_files': ['src/categories_and_mappings.ttl'],
            'target': 'wikidata',
        },
        {
            'source_files': ['src/real_hume_mappings.ttl'],
            'target': 'humord',
        },
        {
            'source_files': ['src/real_tekord_mappings.ttl'],
            'target': 'tekord',
        },
        {
            'source_files': ['src/ccmapper_mappings.ttl'],
            'target': 'ddc23no',
        },
        {
            'source_files': ['src/msc-ubo.mappings.nt'],
            'target': 'msc-ubo',
        },
    ]

    yield {
        'doc': 'Build mapping distributions',
        'basename': 'build-mappings',
        'name': None
    }

    for mapping_set in mapping_sets:
        yield data_ub_tasks.build_mappings_gen(
            mapping_set['source_files'],
            'dist/%s-%s.mappings.nt' % (config['basename'], mapping_set['target']),
            src_uri
        )

def task_build_json():
    return data_ub_tasks.gen_solr_json(config, 'realfagstermer')


def task_elasticsearch():
    return data_ub_tasks.gen_elasticsearch(config, 'realfagstermer')


def task_git_push():
    return data_ub_tasks.git_push_task_gen(config)


def task_publish_dumps():
    return data_ub_tasks.publish_dumps_task_gen(config['dumps_dir'], [
        '%s.marc21.xml' % config['basename'],
        '%s.ccmapper.marc21.xml' % config['basename'],
        '%s.ttl' % config['basename'],
        '%s.complete.ttl' % config['basename'],
        '%s.complete.nt' % config['basename'],
        '%s-wikidata.mappings.nt' % config['basename'],
        '%s-humord.mappings.nt' % config['basename'],
        '%s-tekord.mappings.nt' % config['basename'],
        '%s-ddc23no.mappings.nt' % config['basename'],
        '%s-msc-ubo.mappings.nt' % config['basename'],
    ])


def task_fuseki():
    return data_ub_tasks.fuseki_task_gen(config, ['dist/%(basename)s.complete.ttl'])


# def task_nynorsk_liste():

#     def build_table(task):
#         graph = Graph()
#         graph.load('dist/realfagstermer.ttl', format='turtle')
#         concepts = {}
#         for tr in graph.triples_choices((None, [SKOS.prefLabel, SKOS.altLabel], None)):
#             uri = str(tr[0])
#             term = tr[2].value
#             lang = tr[2].language
#             if uri not in concepts:
#                 concepts[uri] = {'pref': {}, 'alt': {}}
#             if tr[1] == SKOS.prefLabel:
#                 concepts[uri]['pref'][lang] = term
#             else:
#                 concepts[uri]['alt'][lang] = concepts[uri]['alt'].get(lang, []) + [term]

#         with open('dist/realfagstermer_bm-nn.csv', 'wb') as f:
#             writer = csv.writer(f, delimiter =',', quotechar ='"',quoting=csv.QUOTE_MINIMAL)
#             writer.writerow([
#                 'URI for begrepet',
#                 'Foretrukket term (bokmål)',
#                 'Foretrukken term (nynorsk)',
#                 'Alternative termer (bokmål)',
#                 'Alternative termar (nynorsk)'
#             ])
#             for k, v in concepts.items():
#                 pbm = v['pref'].get('nb')
#                 pnn = v['pref'].get('nn')
#                 if pbm is not None and pnn is not None:
#                     abm = '|'.join(v['alt'].get('nb', []))
#                     ann = '|'.join(v['alt'].get('nn', []))
#                     writer.writerow([
#                         k.encode('utf-8'),
#                         pbm.encode('utf-8'),
#                         pnn.encode('utf-8'),
#                         abm.encode('utf-8'),
#                         ann.encode('utf-8')
#                     ])
#                 else:
#                     pass  # for now..

#     return {
#         'doc': 'Build bokmaal-nynorsk list',
#         'actions': [build_table],
#         'file_dep': [
#             'src/nynorsk.ttl',
#             'dist/realfagstermer.ttl'
#         ],
#         'targets': [
#             'dist/realfagstermer_bm-nn.csv'
#         ]
#     }


def task_stats():

    # Note: We cannot import rdflib namespaces globally because doit
    # think they are task creator classes because
    # hasattr(Namespace, 'create_doit_tasks') evaluates to True, since
    # a namespace can include *any* value.
    from rdflib.namespace import SKOS

    def stats_from_graph(g):

        facets = {
            'Topic': {
                'concepts': 0,
                'terms': 0,
                'prefLabels': {'nb': 0, 'nn': 0, 'en': 0, 'la': 0},
                'altLabels': {'nb': 0, 'nn': 0, 'en': 0, 'la': 0}
            },
            'Time': {
                'concepts': 0,
                'terms': 0,
                'prefLabels': {'nb': 0, 'nn': 0, 'en': 0, 'la': 0},
                'altLabels': {'nb': 0, 'nn': 0, 'en': 0, 'la': 0}
            },
            'Place': {
                'concepts': 0,
                'terms': 0,
                'prefLabels': {'nb': 0, 'nn': 0, 'en': 0, 'la': 0},
                'altLabels': {'nb': 0, 'nn': 0, 'en': 0, 'la': 0}
            },
            'GenreForm': {
                'concepts': 0,
                'terms': 0,
                'prefLabels': {'nb': 0, 'nn': 0, 'en': 0, 'la': 0},
                'altLabels': {'nb': 0, 'nn': 0, 'en': 0, 'la': 0}
            },
            'CompoundConcept': {
                'concepts': 0,
                'terms': 0,
                'prefLabels': {}
            },
            'VirtualCompoundConcept': {
                'concepts': 0,
                'terms': 0,
                'prefLabels': {}
            }
        }

        features = {
            'definition': 0,
            'editorialNote': 0,
            'related': 0,
            'exactMatch': 0,
            'closeMatch': 0,
            'relatedMatch': 0,
            'broadMatch': 0,
            'narrowMatch': 0,
        }

        mappingUris = {
            'agrovoc': 'http://aims.fao.org/aos/agrovoc/',
            'ddc': 'http://dewey.info/',
            'tekord': 'http://data.ub.uio.no/tekord/',
            'wikidata': 'http://www.wikidata.org/',
            'humord': 'http://data.ub.uio.no/humord',
        }

        mappings = {
            'agrovoc': 0,
            'ddc': 0,
            'tekord': 0,
            'humord': 0,
            'wikidata': 0,
        }

        for x in g.triples_choices((None, [SKOS.mappingRelation], None)):
            if type(x[2]) == URIRef:
                uri = str(x[2])
                for k, v in mappingUris.items():
                    if uri.startswith(v):
                        mappings[k] += 1

        for featureName in features.keys():

            vals = g.query(u"""PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            PREFIX mads: <http://www.loc.gov/mads/rdf/v1#>
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            SELECT (COUNT(DISTINCT ?o) AS ?c)
            WHERE {
              ?s skos:%s ?o
              FILTER NOT EXISTS { ?s owl:deprecated true }
            }""" % featureName).bindings[0].values()

            features[featureName] = int(list(vals)[0].value)

        terms = {}
        for triple in g.triples_choices((None, [SKOS.prefLabel, SKOS.altLabel], None)):
            lang = triple[2].language
            if lang not in terms:
                terms[lang] = 0
            terms[lang] += 1

        terms['_sum'] = sum([v for x, v in terms.items()])

        sumConcepts = 0
        sumConceptsWithStrings = 0

        vals = g.query(u"""PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            PREFIX ubo: <http://data.ub.uio.no/onto#>
            PREFIX owl: <http://www.w3.org/2002/07/owl#>

            SELECT (COUNT(DISTINCT ?s) AS ?c)
            WHERE {
              ?s owl:deprecated true .
        }""").bindings[0].values()
        deprecatedConcepts = int(list(vals)[0].value)

        for facetName, facet in facets.items():

            vals = g.query(u"""PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            PREFIX ubo: <http://data.ub.uio.no/onto#>
            PREFIX owl: <http://www.w3.org/2002/07/owl#>

            SELECT (COUNT(DISTINCT ?s) AS ?c)
            WHERE {
              ?s a ubo:%s .
              FILTER NOT EXISTS { ?s owl:deprecated true } .
            }""" % (facetName)).bindings[0].values()
            facets[facetName]['concepts'] = int(list(vals)[0].value)

            sumConceptsWithStrings += facets[facetName]['concepts']

            if facetName is not 'CompoundConcept' and facetName is not 'VirtualCompoundConcept':
                sumConcepts += facets[facetName]['concepts']

            facets[facetName]['terms'] = 0

            for langName in facet['prefLabels'].keys():

                vals = g.query(u"""PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
                PREFIX ubo: <http://data.ub.uio.no/onto#>
                PREFIX owl: <http://www.w3.org/2002/07/owl#>

                SELECT (COUNT(DISTINCT ?o) AS ?c)
                WHERE {
                  ?s a ubo:%s .
                  ?s skos:prefLabel ?o .
                  FILTER(langMatches(lang(?o), "%s"))
                  FILTER NOT EXISTS { ?s owl:deprecated true } .
                }""" % (facetName, langName)).bindings[0].values()
                facets[facetName]['prefLabels'][langName] = int(list(vals)[0].value)

                vals = g.query(u"""PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
                PREFIX ubo: <http://data.ub.uio.no/onto#>
                PREFIX owl: <http://www.w3.org/2002/07/owl#>

                SELECT (COUNT(DISTINCT ?o) AS ?c)
                WHERE {
                  ?s a ubo:%s .
                  ?s skos:altLabel ?o .
                  FILTER(langMatches(lang(?o), "%s"))
                  FILTER NOT EXISTS { ?s owl:deprecated true } .
                }""" % (facetName, langName)).bindings[0].values()
                facets[facetName]['altLabels'][langName] = int(list(vals)[0].value)

                facets[facetName]['terms'] += facets[facetName]['prefLabels'][langName] + facets[facetName]['altLabels'][langName]

        return {
            'deprecatedConcepts': deprecatedConcepts,
            'concepts': sumConceptsWithStrings,
            'conceptsWithoutStrings': sumConcepts,
            'terms': terms,
            'facets': facets,
            'features': features,
            'mappings': mappings
        }

    def stats(task):

        t0 = time.time()

        g = Graph()
        g.load('dist/realfagstermer.complete.ttl', format='turtle')

        s = json.load(open('realfagstermer.github.io/_data/stats.json', 'r'))
        current = stats_from_graph(g)
        current['ts'] = now = int(time.time())
        s.append(current)

        json.dump(current, open('realfagstermer.github.io/_data/stats_current.json', 'w'), indent=2, sort_keys=True)
        json.dump(s, open('realfagstermer.github.io/_data/stats.json', 'w'), indent=2, sort_keys=True)

        dt = time.time() - t0
        logger.info('Generated stats in %.1f seconds', dt)


    return {
        'doc': 'Generate stats',
        'actions': [
            'test -d realfagstermer.github.io || git clone git@github.com:realfagstermer/realfagstermer.github.io.git',
            'cd realfagstermer.github.io && git pull && cd ..',
            stats,
            'cd realfagstermer.github.io && git add _data/stats_current.json _data/stats.json',
            'cd realfagstermer.github.io && git commit -m "Update stats"',
            'cd realfagstermer.github.io && git push origin',
        ],
        'file_dep': [
            'dist/realfagstermer.complete.ttl'
        ],
        'targets': [
            'realfagstermer.github.io/_data/stats.json',
            'realfagstermer.github.io/_data/stats_current.json'
        ]
    }
