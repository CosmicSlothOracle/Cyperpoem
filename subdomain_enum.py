#!/usr/bin/env python3
"""
Subdomain Enumeration Tool for Attack Surface Analysis
Part 1: Discover subdomains from root domains
"""

import asyncio
import aiohttp
import aiofiles
import aiodns
import json
import sys
import argparse
from pathlib import Path
from typing import Set, List, Tuple, Optional
from dataclasses import dataclass
import subprocess
import random


@dataclass
class SubdomainResult:
    subdomain: str
    record_type: str
    target: str
    is_valid: bool


class SubdomainEnumerator:
    """Multi-technique subdomain enumeration"""

    DNS_RESOLVERS = ['8.8.8.8', '8.8.4.4']  # Google's DNS

    COMMON_SUBDOMAINS = [
        'www', 'mail', 'ftp', 'localhost', 'webmail', 'smtp', 'pop', 'ns1', 'webdisk',
        'ns2', 'cpanel', 'whm', 'autodiscover', 'autoconfig', 'ns3', 'm', 'imap',
        'test', 'ns', 'blog', 'pop3', 'dev', 'www2', 'admin', 'forum', 'news',
        'vpn', 'ns4', 'www1', 'mail2', 'new', 'mysql', 'old', 'lists', 'support',
        'mobile', 'mx', 'static', 'docs', 'beta', 'shop', 'sql', 'secure', 'demo',
        'cp', 'calendar', 'wiki', 'web', 'media', 'email', 'pda', 'mg', 'ts',
        'staging', 'api', 'chat', 'search', 'mail1', '157', '192', 'img', 'tls',
        'alt', 'ex', 'sv', 'mail3', 'get', 'analytics', 'jira', 'gitlab', 'grafana',
        'prometheus', 'kibana', 'elasticsearch', 'jenkins', 'nexus', 'registry',
        'registry-1', 'registry1', 'docker', 'kubernetes', 'k8s', 'kube', 'api-v1',
        'api-v2', 'api-v3', 'v1', 'v2', 'v3', 'staging-api', 'prod-api', 'dev-api',
        'preview', 'alpha', 'canary', 'edge', 'cdn', 'static1', 'static2', 'assets',
        'images', 'js', 'css', 'fonts', 'uploads', 'files', 'storage', 's3', 'bucket',
        'backup', 'archive', 'db', 'database', 'postgres', 'mysql', 'redis', 'mongo',
        'elasticsearch', 'kafka', 'rabbitmq', 'queue', 'worker', 'cron', 'scheduler',
        'job', 'task', 'async', 'ws', 'websocket', 'socket', 'io', 'realtime',
        'push', 'notify', 'notification', 'alert', 'monitor', 'monitoring', 'status',
        'health', 'ping', 'ready', 'live', 'metrics', 'prometheus', 'grafana',
        'influxdb', 'telegraf', 'nagios', 'zabbix', 'prtg', 'datadog', 'newrelic',
        'sentry', 'bugsnag', 'rollbar', 'log', 'logs', 'logging', 'trace',
        'tracing', 'zipkin', 'jaeger', 'apm', 'auth', 'login', 'sso', 'oauth',
        'openid', 'saml', 'idp', 'identity', 'accounts', 'user', 'users', 'profile',
        'dashboard', 'panel', 'console', 'portal', 'admin', 'administrator',
        'root', 'superuser', 'manage', 'management', 'config', 'configuration',
        'settings', 'env', 'environment', 'vars', 'secrets', 'vault', 'kms',
        'key', 'keys', 'cert', 'certs', 'certificate', 'ssl', 'tls', 'https',
        'security', 'firewall', 'waf', 'shield', 'guard', 'protect', 'scan',
        'scanner', 'audit', 'compliance', 'pentest', 'vuln', 'vulnerability',
        'cve', 'exploit', 'malware', 'virus', 'threat', 'intel', 'osint',
        'recon', 'reconnaissance', 'discover', 'map', 'survey', 'inventory',
        'asset', 'assets', 'cmdb', 'itam', 'itsm', 'service', 'servicedesk',
        'helpdesk', 'support', 'ticket', 'tickets', 'issue', 'issues', 'bug',
        'bugs', 'feature', 'features', 'request', 'requests', 'feedback',
        'survey', 'poll', 'vote', 'rating', 'review', 'reviews', 'comment',
        'comments', 'social', 'community', 'forum', 'boards', 'thread', 'threads',
        'post', 'posts', 'article', 'articles', 'blog', 'blogs', 'news',
        'press', 'media', 'pr', 'marketing', 'ads', 'advertising', 'campaign',
        'promo', 'promotion', 'sale', 'sales', 'shop', 'store', 'cart', 'checkout',
        'payment', 'pay', 'billing', 'invoice', 'order', 'orders', 'shipping',
        'delivery', 'track', 'tracking', 'returns', 'refund', 'exchange',
        'warranty', 'service', 'services', 'repair', 'maintenance', 'parts',
        'accessories', 'merch', 'merchandise', 'gift', 'gifts', 'coupon',
        'discount', 'deal', 'deals', 'offer', 'offers', 'flash', 'clearance',
        'outlet', 'wholesale', 'bulk', 'b2b', 'partner', 'partners', 'affiliate',
        'reseller', 'distributor', 'vendor', 'supplier', 'supply', 'chain',
        'procurement', 'purchase', 'purchasing', 'buy', 'buyer', 'sourcing',
        'rfq', 'rfp', 'tender', 'bid', 'bidding', 'auction', 'marketplace',
        'exchange', 'trade', 'trading', 'broker', 'dealer', 'agent', 'agency',
        'rep', 'representative', 'salesrep', 'account', 'accounts', 'client',
        'clients', 'customer', 'customers', 'consumer', 'consumers', 'user',
        'member', 'members', 'subscriber', 'subscribers', 'audience', 'visitor',
        'guest', 'public', 'private', 'internal', 'external', 'intranet',
        'extranet', 'dmz', 'lan', 'wan', 'network', 'net', 'wifi', 'wireless',
        'hotspot', 'access', 'point', 'ap', 'router', 'switch', 'hub', 'bridge',
        'gateway', 'proxy', 'proxies', 'cache', 'caching', 'loadbalancer', 'lb',
        'balancer', 'ha', 'failover', 'cluster', 'node', 'nodes', 'master',
        'slave', 'replica', 'replication', 'primary', 'secondary', 'standby',
        'backup', 'dr', 'disaster', 'recovery', 'bc', 'business', 'continuity',
        'snapshot', 'clone', 'mirror', 'sync', 'async', 'replicate', 'copy',
        'duplicate', 'fork', 'branch', 'merge', 'build', 'ci', 'cd', 'pipeline',
        'deploy', 'deployment', 'release', 'version', 'artifact', 'package',
        'rpm', 'deb', 'msi', 'exe', 'bin', 'binary', 'source', 'src', 'git',
        'svn', 'mercurial', 'hg', 'cvs', 'repo', 'repository', 'project',
        'module', 'component', 'library', 'lib', 'sdk', 'toolkit', 'framework',
        'runtime', 'vm', 'virtual', 'machine', 'instance', 'server', 'host',
        'container', 'docker', 'pod', 'service', 'svc', 'endpoint', 'ep',
        'ingress', 'egress', 'gateway', 'mesh', 'istio', 'linkerd', 'consul',
        'vault', 'nomad', 'terraform', 'ansible', 'puppet', 'chef', 'salt',
        'vagrant', 'packer', 'pulumi', 'crossplane', 'argo', 'flux', 'spinnaker',
        'jenkins', 'bamboo', 'teamcity', 'circleci', 'travis', 'appveyor',
        'github', 'bitbucket', 'gitlab', 'gitea', 'gogs', 'phabricator',
        'bugzilla', 'jira', 'confluence', 'wiki', 'notion', 'slack', 'discord',
        'teams', 'zoom', 'webex', 'meet', 'goto', 'skype', 'hangouts', 'chat',
        'irc', 'xmpp', 'matrix', 'riot', 'element', 'signal', 'telegram',
        'whatsapp', 'line', 'wechat', 'qq', 'alipay', 'pay', 'stripe', 'paypal',
        'square', 'adyen', 'braintree', 'authorize', 'worldpay', 'sagepay',
        'trustly', 'klarna', 'afterpay', 'affirm', 'sezzle', 'quadpay',
        'splitit', 'partial', 'layaway', 'installment', 'emi', 'finance',
        'financing', 'credit', 'debit', 'card', 'bank', 'banking', 'wire',
        'ach', 'sepa', 'swift', 'iban', 'routing', 'account', 'checking',
        'savings', 'deposit', 'loan', 'mortgage', 'invest', 'investment',
        'trade', 'trading', 'portfolio', 'wealth', 'robo', 'advisor', 'plan',
        'planning', 'retire', 'retirement', 'pension', '401k', 'ira', 'super',
        'annuity', 'insurance', 'life', 'health', 'auto', 'home', 'property',
        'casualty', 'liability', 'umbrella', 'flood', 'earthquake', 'disaster',
        'claim', 'claims', 'adjust', 'adjuster', 'underwrite', 'underwriting',
        'policy', 'policies', 'binder', 'endorsement', 'rider', 'exclusion',
        'deductible', 'premium', 'rate', 'rating', 'actuary', 'actuarial',
        'risk', 'assessment', 'score', 'scoring', 'model', 'modeling',
        'forecast', 'forecasting', 'predict', 'prediction', 'predictive',
        'ml', 'ai', 'dl', 'nn', 'deep', 'learning', 'reinforcement', 'rl',
        'supervised', 'unsupervised', 'semi', 'self', 'auto', 'automated',
        'automation', 'robotic', 'rpa', 'process', 'workflow', 'orchestration',
        'choreography', 'saga', 'pattern', 'microservice', 'microservices',
        'monolith', 'legacy', 'modern', 'modernization', 'transform',
        'transformation', 'migrat', 'migration', 'upgrade', 'update', 'patch',
        'hotfix', 'fix', 'resolve', 'solution', 'solve', 'answer', 'respond',
        'response', 'incident', 'problem', 'change', 'cr', 'change', 'request',
        'sr', 'rfc', 'release', 'deployment', 'implementation', 'install',
        'installation', 'setup', 'configure', 'configuration', 'customize',
        'customization', 'personalize', 'personalization', 'theme', 'skin',
        'template', 'layout', 'design', 'style', 'css', 'stylesheet', 'script',
        'javascript', 'typescript', 'coffee', 'dart', 'flutter', 'react',
        'reactjs', 'vue', 'vuejs', 'angular', 'svelte', 'ember', 'backbone',
        'jquery', 'bootstrap', 'tailwind', 'bulma', 'foundation', 'semantic',
        'material', 'ant', 'chakra', 'next', 'nextjs', 'nuxt', 'nuxtjs',
        'gatsby', 'gridsome', 'hugo', 'jekyll', 'hexo', 'middleman', 'eleventy',
        '11ty', 'astro', 'solid', 'solidjs', 'qwik', 'remix', 'redwood',
        'blitz', 't3', 'trpc', 'prisma', 'sequelize', 'typeorm', 'mongoose',
        'orm', 'odm', 'dao', 'dto', 'entity', 'model', 'schema', 'migration',
        'migrate', 'seed', 'seeder', 'factory', 'fixture', 'mock', 'stub',
        'fake', 'faker', 'generate', 'generator', 'scaffold', 'boilerplate',
        'starter', 'template', 'cookiecutter', 'yeoman', 'plop', 'hygen',
        'codegen', 'swagger', 'openapi', 'graphql', 'rest', 'rpc', 'grpc',
        'thrift', 'avro', 'protobuf', 'proto', 'wsdl', 'soap', 'xml', 'json',
        'yaml', 'yml', 'toml', 'ini', 'cfg', 'config', 'conf', 'properties',
        'env', 'dotenv', 'environment', 'variable', 'secret', 'password',
        'pass', 'pwd', 'token', 'key', 'apikey', 'api-key', 'secretkey',
        'secret-key', 'accesskey', 'access-key', 'privatekey', 'private-key',
        'publickey', 'public-key', 'sshkey', 'ssh-key', 'gpgkey', 'gpg-key',
        'pgp', 'certificate', 'cert', 'crt', 'pem', 'der', 'p12', 'pfx',
        'keystore', 'truststore', 'jks', 'ca', 'root', 'intermediate',
        'leaf', 'endentity', 'subject', 'issuer', 'crl', 'ocsp', 'stapling',
        'pinning', 'hpkp', 'hsts', 'csp', 'content', 'security', 'policy',
        'xss', 'csrf', 'sqli', 'injection', 'overflow', 'buffer', 'heap',
        'stack', 'memory', 'leak', 'race', 'condition', 'deadlock', 'starvation',
        'livelock', 'semaphore', 'mutex', 'lock', 'spinlock', 'rwlock',
        'barrier', 'condition', 'variable', 'signal', 'wait', 'notify',
        'broadcast', 'thread', 'threads', 'threading', 'process', 'processes',
        'multiprocessing', 'fork', 'exec', 'spawn', 'join', 'detach',
        'daemon', 'service', 'systemd', 'system', 'init', 'rc', 'runlevel',
        'boot', 'startup', 'shutdown', 'reboot', 'restart', 'reload',
        'refresh', 'reset', 'restore', 'recover', 'backup', 'snapshot',
        'checkpoint', 'save', 'load', 'import', 'export', 'migrate',
        'sync', 'synchronize', 'replicate', 'copy', 'clone', 'mirror',
        'shadow', 'standby', 'spare', 'failover', 'switch', 'over',
        'cutover', 'transition', 'transform', 'transit', 'transfer',
        'transmit', 'transport', 'delivery', 'receive', 'receipt',
        'ack', 'acknowledge', 'confirm', 'confirmation', 'verify',
        'verification', 'validate', 'validation', 'check', 'test',
        'testing', 'qa', 'qc', 'quality', 'assurance', 'control',
        'audit', 'compliance', 'regulatory', 'regulation', 'governance',
        'risk', 'management', 'erm', 'grc', 'sox', 'pci', 'dss',
        'gdpr', 'ccpa', 'hipaa', 'ferpa', 'glba', 'sox', 'basel',
        'solvency', 'ii', 'oci', 'pci', 'nist', 'iso', '27001',
        '27002', '27017', '27018', '27701', '22301', '31000',
        '9001', '14001', '45001', '50001', '55001', '80001',
        '20000', '20121', '26000', 'sa', '8000', '14064', '14065',
        '17025', '17065', '19011', '19600', '37001', '37301',
        '39001', '44001', '45003', '46001', '50003', '56002',
        '56003', 'eicc', 'rba', 'psci', 'amfori', 'bsci', 'sedex',
        'smeta', 'wrap', 'sa', 'fla', 'icti', 'c-tpat', 'apec',
        'cbp', 'tpat', 'wco', 'safe', 'framework', 'suppliers',
        'customers', 'partners', 'affiliates', 'resellers',
        'distributors', 'vendors', 'suppliers', 'providers',
        'carriers', 'forwarders', 'brokers', 'agents',
        'representatives', 'consultants', 'contractors',
        'subcontractors', 'freelancers', 'temps', 'interns',
        'volunteers', 'donors', 'sponsors', 'investors',
        'shareholders', 'stakeholders', 'board', 'directors',
        'executives', 'officers', 'management', 'leadership',
        'senior', 'junior', 'associate', 'analyst', 'specialist',
        'coordinator', 'administrator', 'assistant', 'support',
        'representative', 'agent', 'advisor', 'consultant',
        'engineer', 'developer', 'programmer', 'coder', 'architect',
        'designer', 'analyst', 'tester', 'qa', 'devops', 'sre',
        'admin', 'sysadmin', 'dba', 'network', 'security',
        'infosec', 'cyber', 'it', 'ops', 'operations', 'support',
        'helpdesk', 'service', 'desk', 'field', 'onsite', 'remote',
        'telework', 'telecommute', 'virtual', 'digital', 'online',
        'web', 'internet', 'intranet', 'extranet', 'cloud', 'saas',
        'paas', 'iaas', 'daas', 'baas', 'faas', 'serverless',
        'microservices', 'containers', 'kubernetes', 'openshift',
        'rancher', 'mesos', 'dcos', 'swarm', 'compose', 'stack',
        'service', 'mesh', 'istio', 'linkerd', 'consul', 'traefik',
        'nginx', 'apache', 'httpd', 'iis', 'tomcat', 'jetty',
        'undertow', 'wildfly', 'jboss', 'weblogic', 'websphere',
        'glassfish', 'payara', 'resin', 'tomee', 'geronimo',
        'jonas', 'resin', 'caucho', 'jrun', 'coldfusion', 'lucee',
        'railo', 'openbd', 'db', 'data', 'database', 'sql', 'nosql',
        'rdbms', 'relational', 'object', 'oriented', 'graph',
        'document', 'key', 'value', 'column', 'family', 'wide',
        'column', 'store', 'time', 'series', 'tsdb', 'inmemory',
        'cache', 'search', 'engine', 'full', 'text', 'analytics',
        'warehouse', 'datalake', 'lakehouse', 'datahub', 'catalog',
        'lineage', 'governance', 'quality', 'profiling',
        'masking', 'anonymization', 'pseudonymization',
        'encryption', 'tokenization', 'vault', 'hsm', 'kms',
        'secrets', 'manager', 'parameter', 'store', 'config',
        'configuration', 'service', 'discovery', 'registry',
        'consul', 'etcd', 'zookeeper', 'eureka', 'nacos',
        'apollo', 'disconf', 'archaius', 'diamond', 'qconf',
        'ctrip', 'agnes', 'spring', 'cloud', 'config', 'server',
        'bus', 'stream', 'task', 'batch', 'integration', 'gateway',
        'circuit', 'breaker', 'hystrix', 'resilience4j', 'sentinel',
        'ratelimiter', 'quota', 'throttle', 'limit', 'burst',
        'allowance', 'capacity', 'planning', 'sizing', 'estimation',
        'calculation', 'computation', 'processing', 'analytics',
        'analysis', 'mining', 'learning', 'training', 'inference',
        'prediction', 'classification', 'clustering', 'regression',
        'recommendation', 'search', 'ranking', 'scoring',
        'matching', 'similarity', 'distance', 'metric', 'measure',
        'evaluation', 'assessment', 'benchmark', 'comparison',
        'competition', 'challenge', 'contest', 'tournament',
        'match', 'game', 'play', 'player', 'team', 'group',
        'club', 'society', 'association', 'organization',
        'institution', 'foundation', 'trust', 'charity', 'nonprofit',
        'ngo', 'npo', 'volunteer', 'community', 'society',
        'public', 'private', 'sector', 'industry', 'market',
        'economy', 'economics', 'finance', 'financial', 'fiscal',
        'monetary', 'banking', 'investment', 'capital', 'asset',
        'wealth', 'money', 'cash', 'fund', 'funding', 'grant',
        'loan', 'credit', 'debt', 'equity', 'share', 'stock',
        'bond', 'security', 'derivative', 'future', 'option',
        'swap', 'forward', 'spot', 'market', 'exchange', 'trading',
        'trade', 'commerce', 'commercial', 'business', 'corporate',
        'enterprise', 'company', 'firm', 'partnership', 'llc',
        'inc', 'corp', 'limited', 'ltd', 'plc', 'ag', 'gmbh',
        'sarl', 'sas', 'bv', 'nv', 'oy', 'ab', 'as', 'kk', 'co',
        'ltd', 'ltda', 'sa', 'srl', 'spa', 'sapa', 'sc', 'scs',
        'sca', 'sep', 'snc', 'scs', 'sf', 'scop', 'sas', 'sasu',
        'eurl', 'selarl', 'sem', 'snc', 'scs', 'sca', 'sep', 'sf',
        'scop', 'eeig', 'geie', 'ec', 'ei', 'eg', 'aeie', 'gie',
        'ue', 'eu', 'usa', 'us', 'uk', 'gb', 'de', 'fr', 'es',
        'it', 'nl', 'be', 'ch', 'at', 'se', 'no', 'dk', 'fi',
        'pl', 'cz', 'sk', 'hu', 'ro', 'bg', 'hr', 'si', 'ee',
        'lv', 'lt', 'ie', 'pt', 'gr', 'cy', 'mt', 'lu', 'li',
        'mc', 'sm', 'va', 'ad', 'by', 'ua', 'md', 'ru', 'kz',
        'uz', 'tj', 'kg', 'tm', 'ge', 'az', 'am', 'tr', 'il',
        'jo', 'lb', 'sy', 'iq', 'ir', 'sa', 'kw', 'bh', 'qa',
        'ae', 'om', 'ye', 'eg', 'ly', 'tn', 'dz', 'ma', 'mr',
        'ml', 'ne', 'td', 'sd', 'er', 'dj', 'et', 'so', 'ke',
        'ug', 'rw', 'bi', 'tz', 'mw', 'zm', 'zw', 'mz', 'mg',
        'sc', 'mu', 'km', 'ao', 'cd', 'cg', 'ga', 'gq', 'cm',
        'cf', 'td', 'ng', 'bj', 'tg', 'gh', 'ci', 'lr', 'sl',
        'gn', 'gw', 'sn', 'gm', 'cv', 'st', 'gq', 'za', 'ls',
        'sz', 'na', 'bw', 'zw', 'mz', 'zm', 'ao', 'cd', 'tz',
        'ke', 'ug', 'rw', 'bi', 'et', 'er', 'dj', 'so', 'eg',
        'ly', 'tn', 'dz', 'ma', 'mr', 'ml', 'ne', 'td', 'sd',
        'bf', 'ng', 'bj', 'tg', 'gh', 'ci', 'lr', 'sl', 'gn',
        'gw', 'sn', 'gm', 'cv', 'st', 'gq', 'cm', 'cf', 'td',
    ]

    def __init__(self, domains_file: str, output_file: str = "subdomains.txt",
                 max_workers: int = 50):
        self.domains_file = Path(domains_file)
        self.output_file = Path(output_file)
        self.max_workers = max_workers
        self.valid_records = {'A', 'CNAME', 'MX', 'TXT'}
        self.found_subdomains: Set[str] = set()
        self.resolver = None

    async def init_resolver(self):
        """Initialize DNS resolver"""
        self.resolver = aiodns.DNSResolver(
            nameservers=self.DNS_RESOLVERS,
            timeout=5,
            tries=2
        )

    def load_domains(self) -> List[str]:
        """Load root domains from file"""
        with open(self.domains_file, 'r') as f:
            return [line.strip().lower() for line in f if line.strip()]

    async def check_dns_record(self, subdomain: str, record_type: str) -> Optional[SubdomainResult]:
        """Check if a DNS record exists for subdomain"""
        try:
            if record_type == 'A':
                result = await self.resolver.query(subdomain, 'A')
                if result:
                    return SubdomainResult(
                        subdomain=subdomain,
                        record_type='A',
                        target=result[0].host if hasattr(result[0], 'host') else str(result[0]),
                        is_valid=True
                    )
            elif record_type == 'CNAME':
                result = await self.resolver.query(subdomain, 'CNAME')
                if result:
                    return SubdomainResult(
                        subdomain=subdomain,
                        record_type='CNAME',
                        target=result.cname if hasattr(result, 'cname') else str(result),
                        is_valid=True
                    )
            elif record_type == 'MX':
                result = await self.resolver.query(subdomain, 'MX')
                if result:
                    return SubdomainResult(
                        subdomain=subdomain,
                        record_type='MX',
                        target=result[0].host if hasattr(result[0], 'host') else str(result[0]),
                        is_valid=True
                    )
            elif record_type == 'TXT':
                result = await self.resolver.query(subdomain, 'TXT')
                if result:
                    return SubdomainResult(
                        subdomain=subdomain,
                        record_type='TXT',
                        target=str(result[0]) if result else "",
                        is_valid=True
                    )
        except aiodns.error.DNSError as e:
            if e.args[0] != aiodns.error.ARES_ENOTFOUND:
                pass  # Ignore other errors
        except Exception:
            pass
        return None

    async def enumerate_subdomain(self, prefix: str, domain: str) -> Optional[SubdomainResult]:
        """Enumerate a single subdomain with all record types"""
        subdomain = f"{prefix}.{domain}" if prefix else domain

        for record_type in self.valid_records:
            result = await self.check_dns_record(subdomain, record_type)
            if result and result.is_valid:
                return result
        return None

    async def enumerate_domain(self, domain: str, progress_queue: asyncio.Queue):
        """Enumerate all subdomains for a single domain"""
        tasks = []
        semaphore = asyncio.Semaphore(self.max_workers)

        async def bounded_check(prefix: str, domain: str):
            async with semaphore:
                result = await self.enumerate_subdomain(prefix, domain)
                if result:
                    await progress_queue.put(('found', result))
                return result

        # Add empty prefix (root domain itself)
        tasks.append(bounded_check('', domain))

        # Add common subdomains
        for prefix in self.COMMON_SUBDOMAINS:
            tasks.append(bounded_check(prefix, domain))

        # Add numeric prefixes
        for i in range(1, 100):
            tasks.append(bounded_check(str(i), domain))
            tasks.append(bounded_check(f'www{i}', domain))
            tasks.append(bounded_check(f'mail{i}', domain))
            tasks.append(bounded_check(f'ns{i}', domain))
            tasks.append(bounded_check(f'server{i}', domain))
            tasks.append(bounded_check(f'host{i}', domain))
            tasks.append(bounded_check(f'node{i}', domain))
            tasks.append(bounded_check(f'app{i}', domain))
            tasks.append(bounded_check(f'api{i}', domain))
            tasks.append(bounded_check(f'db{i}', domain))

        # Add environment prefixes
        env_prefixes = ['dev', 'development', 'stg', 'staging', 'prod', 'production',
                       'test', 'testing', 'uat', 'qa', 'preprod', 'preview', 'demo']
        for env in env_prefixes:
            tasks.append(bounded_check(env, domain))
            for prefix in self.COMMON_SUBDOMAINS[:20]:
                tasks.append(bounded_check(f"{prefix}-{env}", domain))
                tasks.append(bounded_check(f"{env}-{prefix}", domain))

        # Add regional prefixes
        regions = ['us', 'eu', 'asia', 'na', 'sa', 'au', 'uk', 'de', 'fr', 'jp',
                   'east', 'west', 'north', 'south', 'central']
        for region in regions:
            tasks.append(bounded_check(region, domain))
            for prefix in ['api', 'app', 'cdn', 'media', 'static', 'www', 'mail']:
                tasks.append(bounded_check(f"{prefix}-{region}", domain))
                tasks.append(bounded_check(f"{region}-{prefix}", domain))

        await asyncio.gather(*tasks, return_exceptions=True)
        await progress_queue.put(('done', domain))

    async def run_enumeration(self):
        """Run full enumeration"""
        await self.init_resolver()
        domains = self.load_domains()

        print(f"[*] Loaded {len(domains)} root domains")
        print(f"[*] Starting subdomain enumeration with {self.max_workers} workers")

        progress_queue = asyncio.Queue()
        domain_tasks = [self.enumerate_domain(d, progress_queue) for d in domains]

        # Progress reporter
        completed = 0
        total = len(domains)

        async def report_progress():
            nonlocal completed
            while completed < total:
                msg_type, data = await progress_queue.get()
                if msg_type == 'found':
                    self.found_subdomains.add(data.subdomain)
                    print(f"[+] Found: {data.subdomain} ({data.record_type} -> {data.target})")
                elif msg_type == 'done':
                    completed += 1
                    if completed % 10 == 0 or completed == total:
                        print(f"[*] Progress: {completed}/{total} domains completed")

        # Run enumeration and progress reporting concurrently
        await asyncio.gather(
            asyncio.gather(*domain_tasks, return_exceptions=True),
            report_progress()
        )

        # Save results
        self.save_results()

    def save_results(self):
        """Save discovered subdomains to file"""
        sorted_subdomains = sorted(self.found_subdomains)
        with open(self.output_file, 'w') as f:
            for subdomain in sorted_subdomains:
                f.write(f"{subdomain}\n")
        print(f"\n[+] Saved {len(sorted_subdomains)} subdomains to {self.output_file}")

    def verify_with_dig(self, subdomain: str) -> bool:
        """Verify subdomain using dig command"""
        try:
            for record_type in self.valid_records:
                result = subprocess.run(
                    ['dig', f'@{self.DNS_RESOLVERS[0]}', subdomain, record_type, '+short'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.stdout.strip() and 'NXDOMAIN' not in result.stdout:
                    return True
        except Exception:
            pass
        return False


def main():
    parser = argparse.ArgumentParser(description='Subdomain Enumeration Tool')
    parser.add_argument('-d', '--domains', default='domains.txt',
                       help='File containing root domains')
    parser.add_argument('-o', '--output', default='subdomains.txt',
                       help='Output file for discovered subdomains')
    parser.add_argument('-w', '--workers', type=int, default=50,
                       help='Number of concurrent workers')

    args = parser.parse_args()

    enumerator = SubdomainEnumerator(
        domains_file=args.domains,
        output_file=args.output,
        max_workers=args.workers
    )

    try:
        asyncio.run(enumerator.run_enumeration())
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user")
        enumerator.save_results()


if __name__ == '__main__':
    main()
