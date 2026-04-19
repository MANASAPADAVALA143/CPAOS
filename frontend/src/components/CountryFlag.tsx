const FLAGS: Record<string, string> = {
  India: '🇮🇳',
  UAE: '🇦🇪',
  UK: '🇬🇧',
  US: '🇺🇸',
  Singapore: '🇸🇬',
  Australia: '🇦🇺',
  Other: '🌍',
}

export function CountryFlag({ country }: { country: string }) {
  return <span className="mr-1">{FLAGS[country] ?? '🌍'}</span>
}
