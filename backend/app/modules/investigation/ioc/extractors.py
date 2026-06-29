import re
from typing import List, Tuple
from app.modules.investigation.schemas import NormalizedEventCreate
from app.modules.investigation.ioc.base import BaseIOCExtractor

class IPv4Extractor(BaseIOCExtractor):
    # Matches simple IPv4 (excludes common local/private subnets roughly or strictly just looks for the pattern)
    # Using a standard regex for IPv4
    REGEX = re.compile(r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b')

    def extract(self, event: NormalizedEventCreate) -> List[Tuple[str, str]]:
        iocs = []
        if event.source_ip and self.REGEX.match(event.source_ip):
            iocs.append(("ipv4", event.source_ip))
        if event.destination_ip and self.REGEX.match(event.destination_ip):
            iocs.append(("ipv4", event.destination_ip))
            
        for match in self.REGEX.findall(event.raw_message):
            # Exclude obvious local IPs
            if not match.startswith("127.") and not match.startswith("10.") and not match.startswith("192.168."):
                iocs.append(("ipv4", match))
        return iocs

class IPv6Extractor(BaseIOCExtractor):
    REGEX = re.compile(r'\b(?:[A-F0-9]{1,4}:){7}[A-F0-9]{1,4}\b', re.IGNORECASE)

    def extract(self, event: NormalizedEventCreate) -> List[Tuple[str, str]]:
        iocs = []
        for match in self.REGEX.findall(event.raw_message):
            if match != "0:0:0:0:0:0:0:1":
                iocs.append(("ipv6", match))
        return iocs

class DomainExtractor(BaseIOCExtractor):
    REGEX = re.compile(r'\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b')

    def extract(self, event: NormalizedEventCreate) -> List[Tuple[str, str]]:
        iocs = []
        for match in self.REGEX.findall(event.raw_message):
            match_lower = match.lower()
            if not match_lower.endswith(".local") and not match_lower.endswith(".lan"):
                iocs.append(("domain", match_lower))
        return iocs

class URLExtractor(BaseIOCExtractor):
    REGEX = re.compile(r'\b(?:https?|ftp)://[^\s/$.?#].[^\s]*\b', re.IGNORECASE)

    def extract(self, event: NormalizedEventCreate) -> List[Tuple[str, str]]:
        return [("url", match) for match in self.REGEX.findall(event.raw_message)]

class HashExtractor(BaseIOCExtractor):
    MD5_REGEX = re.compile(r'\b[A-Fa-f0-9]{32}\b')
    SHA1_REGEX = re.compile(r'\b[A-Fa-f0-9]{40}\b')
    SHA256_REGEX = re.compile(r'\b[A-Fa-f0-9]{64}\b')

    def extract(self, event: NormalizedEventCreate) -> List[Tuple[str, str]]:
        iocs = []
        for match in self.MD5_REGEX.findall(event.raw_message):
            iocs.append(("md5", match.lower()))
        for match in self.SHA1_REGEX.findall(event.raw_message):
            iocs.append(("sha1", match.lower()))
        for match in self.SHA256_REGEX.findall(event.raw_message):
            iocs.append(("sha256", match.lower()))
        return iocs

class CVEExtractor(BaseIOCExtractor):
    REGEX = re.compile(r'\bCVE-\d{4}-\d{4,7}\b', re.IGNORECASE)

    def extract(self, event: NormalizedEventCreate) -> List[Tuple[str, str]]:
        return [("cve", match.upper()) for match in self.REGEX.findall(event.raw_message)]

class EmailExtractor(BaseIOCExtractor):
    REGEX = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')

    def extract(self, event: NormalizedEventCreate) -> List[Tuple[str, str]]:
        return [("email", match.lower()) for match in self.REGEX.findall(event.raw_message)]

class HostnameExtractor(BaseIOCExtractor):
    def extract(self, event: NormalizedEventCreate) -> List[Tuple[str, str]]:
        if event.host_name:
            return [("hostname", event.host_name)]
        return []

class UsernameExtractor(BaseIOCExtractor):
    def extract(self, event: NormalizedEventCreate) -> List[Tuple[str, str]]:
        if event.user_name:
            return [("username", event.user_name)]
        return []
