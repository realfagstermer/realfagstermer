# encoding=utf8
from doit import get_var
from roald import Roald
from rdflib.graph import Graph, URIRef
import rdflib.namespace
import csv
import time
import json
import logging
import logging.config
logging.config.fileConfig('logging.cfg', )
logger = logging.getLogger(__name__)

import data_ub_tasks

config = {
    'dumps_dir': get_var('dumps_dir', '/opt/data.ub/www/default/dumps'),
    'dumps_dir_url': get_var('dumps_dir_url', 'http://data.ub.uio.no/dumps'),
    'graph': 'http://data.ub.uio.no/realfagstermer',
    'fuseki': 'http://localhost:3031/ds',
    'basename': 'realfagstermer'
}

DOIT_CONFIG = {
    'default_tasks': [
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
    yield {
        'name': 'git pull',
        'actions': [
            'git config user.name "ubo-bot"',
            'git config user.email "danmichaelo+ubobot@gmail.com"',
            'git pull',
            'git config --unset user.name',
            'git config --unset user.email',
        ]
    }
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
        {'remote': 'https://rawgit.com/scriptotek/data_ub_ontology/master/ub-onto.ttl',
            'local': 'src/ub-onto.ttl'}
    ]:
        yield {
            'name': file['local'],
            'actions': [(data_ub_tasks.fetch_remote, [], {
                'remote': file['remote'],
                'etag_cache': '{}.etag'.format(file['local'])
            })],
            'targets': [file['local']]
        }

def task_fetch_extras():

    yield {
        'doc': 'Fetch remote extra files that have changed',
        'basename': 'fetch-extras',
        'name': None
    }
    for file in [
        {'remote': 'https://mapper.biblionaut.net/export.rdf',
            'local': 'src/mumapper.rdf'},
        {'remote': 'https://lambda.biblionaut.net/export.rdf',
            'local': 'src/lambda.rdf'},
        {'remote': 'https://rawgit.com/realfagstermer/prosjekt-nynorsk/master/data-verified.ttl',
            'local': 'src/nynorsk.ttl'},
    ]:
        yield {
            'name': file['local'],
            'actions': [(data_ub_tasks.fetch_remote, [], {
                'remote': file['remote'],
                'etag_cache': '{}.etag'.format(file['local'])
            })],
            'targets': [file['local']]
        }


def task_build_core():

    def build(task):
        logger.info('Building new core dist')
        roald = Roald()
        roald.load('src/', format='roald2', language='nb')
        roald.set_uri_format(
            'http://data.ub.uio.no/%s/c{id}' % config['basename'])
        roald.save('%s.json' % config['basename'])
        logger.info('Wrote %s.json', config['basename'])

        includes = [
            '%s.scheme.ttl' % config['basename'],
            'src/ub-onto.ttl',
            'src/nynorsk.ttl'
        ]

        # 1) MARC21
        # marc21options = {
        #     'vocabulary_code': 'noubomn',
        #     'created_by': 'NoOU',
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
        'doc': 'Build distribution files (RDF/SKOS + MARC21XML) from source files',
        'basename': 'build-core',
        'actions': [build],
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
        roald.set_uri_format(
            'http://data.ub.uio.no/%s/c{id}' % config['basename'])

        includes = [
            '%s.scheme.ttl' % config['basename'],
            'src/ub-onto.ttl',
            'src/nynorsk.ttl'
        ]

        mappings = [
            'src/mumapper.rdf',
            'src/lambda.rdf'
        ]

        # 1) MARC21
        marc21options = {
            'vocabulary_code': 'noubomn',
            'created_by': 'NoOU',
            'mappings_from': ['src/lambda.rdf']
        }
        roald.export('dist/%s.marc21.xml' %
                     config['basename'], format='marc21', **marc21options)
        logger.info('Wrote dist/%s.marc21.xml', config['basename'])

        # 3) RDF (core + mappings)
        roald.export('dist/%s.complete.ttl' % config['basename'],
                     format='rdfskos',
                     include=includes,
                     mappings_from=mappings
                     )
        logger.info('Wrote dist/%s.complete.ttl', config['basename'])

    return {
        'doc': 'Build distribution files (RDF/SKOS + MARC21XML) from source files',
        'basename': 'build-extras',
        'actions': [build],
        'file_dep': [
            'src/idtermer.txt',
            'src/idsteder.txt',
            'src/idformer.txt',
            'src/idtider.txt',
            'src/idstrenger.txt',
            'src/mumapper.rdf',
            'src/lambda.rdf',
            'src/nynorsk.ttl',
            'src/ub-onto.ttl',
            '%s.scheme.ttl' % config['basename']
        ],
        'targets': [
            'dist/%s.marc21.xml' % config['basename'],
            'dist/%s.complete.ttl' % config['basename']
        ]
    }


def task_build_json():
    return data_ub_tasks.gen_solr_json(config, 'realfagstermer')


def task_git_push():
    return data_ub_tasks.git_push_task_gen(config)


def task_publish_dumps():
    return data_ub_tasks.publish_dumps_task_gen(config['dumps_dir'], [
        '%s.marc21.xml' % config['basename'],
        '%s.ttl' % config['basename'],
        '%s.complete.ttl' % config['basename']
    ])


def task_fuseki():
    return data_ub_tasks.fuseki_task_gen(config, ['dist/%(basename)s.complete.ttl'])


def task_nynorsk_liste():

    def build_table(task):
        graph = Graph()
        graph.load('dist/realfagstermer.ttl', format='turtle')
        concepts = {}
        for tr in graph.triples_choices((None, [rdflib.namespace.SKOS.prefLabel, rdflib.namespace.SKOS.altLabel], None)):
            uri = str(tr[0])
            term = tr[2].value
            lang = tr[2].language
            if uri not in concepts:
                concepts[uri] = {'pref': {}, 'alt': {}}
            if tr[1] == rdflib.namespace.SKOS.prefLabel:
                concepts[uri]['pref'][lang] = term
            else:
                concepts[uri]['alt'][lang] = concepts[uri]['alt'].get(lang, []) + [term]

        with open('dist/realfagstermer_bm-nn.csv', 'wb') as f:
            writer = csv.writer(f, delimiter =',', quotechar ='"',quoting=csv.QUOTE_MINIMAL)
            writer.writerow([
                'URI for begrepet',
                'Foretrukket term (bokmål)',
                'Foretrukken term (nynorsk)',
                'Alternative termer (bokmål)',
                'Alternative termar (nynorsk)'
            ])
            for k, v in concepts.items():
                pbm = v['pref'].get('nb')
                pnn = v['pref'].get('nn')
                if pbm is not None and pnn is not None:
                    abm = '|'.join(v['alt'].get('nb', []))
                    ann = '|'.join(v['alt'].get('nn', []))
                    writer.writerow([
                        k.encode('utf-8'),
                        pbm.encode('utf-8'),
                        pnn.encode('utf-8'),
                        abm.encode('utf-8'),
                        ann.encode('utf-8')
                    ])
                else:
                    pass  # for now..

    return {
        'doc': 'Build bokmaal-nynorsk list',
        'actions': [build_table],
        'file_dep': [
            'src/nynorsk.ttl',
            'dist/realfagstermer.ttl'
        ],
        'targets': [
            'dist/realfagstermer_bm-nn.csv'
        ]
    }


def task_stats():

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
            'ddc': 'http://data.ub.uio.no/ddc/',
            'tekord': 'http://data.ub.uio.no/tekord/'
        }

        mappings = {
            'agrovoc': 0,
            'ddc': 0,
            'tekord': 0
        }

        for x in g.triples_choices((None, [rdflib.namespace.SKOS.exactMatch, rdflib.namespace.SKOS.closeMatch, rdflib.namespace.SKOS.relatedMatch, rdflib.namespace.SKOS.broadMatch, rdflib.namespace.SKOS.narrowMatch], None)):
            if type(x[2]) == URIRef:
                uri = str(x[2])
                for k, v in mappingUris.items():
                    if uri.startswith(v):
                        mappings[k] += 1

        for featureName in features.keys():

            features[featureName] = int(g.query(u"""PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            PREFIX mads: <http://www.loc.gov/mads/rdf/v1#>
            SELECT (COUNT(DISTINCT ?o) AS ?c)
            WHERE {
              ?s skos:%s ?o
            }""" % featureName).bindings[0].values()[0].value)

        terms = {}
        for triple in g.triples_choices((None, [rdflib.namespace.SKOS.prefLabel, rdflib.namespace.SKOS.altLabel], None)):
            lang = triple[2].language
            if lang not in terms:
                terms[lang] = 0
            terms[lang] += 1

        terms['_sum'] = sum([v for x, v in terms.items()])

        sumConcepts = 0
        sumConceptsWithStrings = 0

        for facetName, facet in facets.items():

            facets[facetName]['concepts'] = int(g.query(u"""PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            PREFIX ubo: <http://data.ub.uio.no/onto#>
            SELECT (COUNT(DISTINCT ?s) AS ?c)
            WHERE {
              ?s a ubo:%s .
            }""" % (facetName)).bindings[0].values()[0].value)

            sumConceptsWithStrings += facets[facetName]['concepts']

            if facetName is not 'CompoundConcept' and facetName is not 'VirtualCompoundConcept':
                sumConcepts += facets[facetName]['concepts']

            facets[facetName]['terms'] = 0

            for langName in facet['prefLabels'].keys():

                facets[facetName]['prefLabels'][langName] = int(g.query(u"""PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
                PREFIX ubo: <http://data.ub.uio.no/onto#>
                SELECT (COUNT(DISTINCT ?o) AS ?c)
                WHERE {
                  ?s a ubo:%s .
                  ?s skos:prefLabel ?o .
                  FILTER(langMatches(lang(?o), "%s"))
                }""" % (facetName, langName)).bindings[0].values()[0].value)

                facets[facetName]['altLabels'][langName] = int(g.query(u"""PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
                PREFIX ubo: <http://data.ub.uio.no/onto#>
                SELECT (COUNT(DISTINCT ?o) AS ?c)
                WHERE {
                  ?s a ubo:%s .
                  ?s skos:altLabel ?o .
                  FILTER(langMatches(lang(?o), "%s"))
                }""" % (facetName, langName)).bindings[0].values()[0].value)

                facets[facetName]['terms'] += facets[facetName]['prefLabels'][langName] + facets[facetName]['altLabels'][langName]

        return {
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
            'cd realfagstermer.github.io && git push --mirror origin',  # locally updated refs will be force updated on the remote end !
        ],
        'file_dep': [
            'dist/realfagstermer.complete.ttl'
        ],
        'targets': [
            'realfagstermer.github.io/_data/stats.json'
            'realfagstermer.github.io/_data/stats_current.json'
        ]
    }
