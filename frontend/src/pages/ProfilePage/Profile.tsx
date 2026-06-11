import { useState, useEffect, useRef, type ChangeEvent } from "react";
import "./Profile.css";
import { ProfileImg } from "@/shared";
import type { Profile } from "./lib/profileInterface";
import { fetchProfileInfo } from "@/features/getProfileInfo/getProfileInfo";
import { useNavigate } from "react-router-dom";

export default function Profile() {
	const navigate = useNavigate();

	const [profile, setProfile] = useState<Profile | null>(null);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);

	const [currentImg, setCurrentImg] = useState<string>(ProfileImg);
	const fileInputRef = useRef<HTMLInputElement>(null);

	useEffect(() => {
		const controller = new AbortController();

		const loadProfile = async () => {
			try {
				setLoading(true);
				setError(null);

				const data = await fetchProfileInfo(controller.signal);
				setProfile(data);

				setCurrentImg((prev) => {
					if (prev.startsWith("blob:")) return prev;
					return data.avatarUrl || ProfileImg;
				});
			} catch (error) {
				if (error instanceof Error && error.name === "AbortError") {
					console.log("Abort Error");
					return;
				}

				if (
					error instanceof Error &&
					error.message === "Unauthorized"
				) {
					console.log("Unauthorized");
					navigate("/login", { replace: true });
					return;
				}

				setError("Failed to load profile information");
			} finally {
				setLoading(false);
			}
		};

		loadProfile();

		return () => {
			controller.abort();
		};
	}, [navigate]);

	useEffect(() => {
		return () => {
			if (currentImg.startsWith("blob:")) {
				URL.revokeObjectURL(currentImg);
			}
		};
	}, [currentImg]);

	const handleImgClick = () => {
		fileInputRef.current?.click();
	};

	const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
		const file = e.target.files?.[0];
		if (!file) return;

		const allowedTypes = ["image/png", "image/jpeg"];
		if (!allowedTypes.includes(file.type)) {
			alert("Пожалуйста, выберите файл в формате PNG или JPG");
			e.target.value = "";
			return;
		}

		if (currentImg.startsWith("blob:")) {
			URL.revokeObjectURL(currentImg);
		}

		const newUrl = URL.createObjectURL(file);
		setCurrentImg(newUrl);
	};

	const formatDate = (value: string | null) => {
		if (!value) {
			return "n/a";
		}

		const date = new Date(value);
		if (Number.isNaN(date.getTime())) {
			return value;
		}

		return new Intl.DateTimeFormat("en-GB", {
			dateStyle: "medium",
			timeStyle: "short",
		}).format(date);
	};

	if (loading) {
		return <div>Loading...</div>;
	}

	if (error) {
		return <div>{error}</div>;
	}

	if (!profile) {
		return <div>No profile data</div>;
	}

	const completedTotal =
		profile.tasksCompleted.easy +
		profile.tasksCompleted.medium +
		profile.tasksCompleted.hard;

	const averageSummary = Math.round(
		(profile.averageGrade.easy +
			profile.averageGrade.medium +
			profile.averageGrade.hard) /
			3,
	);

	return (
		<section className="profile-page">
			<div className="profile-shell">
				<section className="profile-hero box-light">
					<div className="profile-hero-main">
						<div className="profile-avatar-block">
							<img
								className="profile-avatar"
								src={currentImg}
								alt="Profile Image"
								width={219}
								height={219}
								onClick={handleImgClick}
							/>
							<p className="profile-avatar-note">
								Click the avatar to update it
							</p>
						</div>

						<input
							type="file"
							accept="image/png, image/jpeg"
							ref={fileInputRef}
							onChange={handleFileChange}
							style={{ display: "none" }}
							data-testid="avatar-input"
						/>

						<div className="profile-hero-copy">
							<div className="profile-hero-header">
								<div>
									<p className="profile-kicker">Profile overview</p>
									<h1 className="profile-name">{profile.username}</h1>
									<p className="profile-email">{profile.email}</p>
								</div>
								<button className="btn-settings-profile btn-ghost">
									Settings
								</button>
							</div>

							<div className="profile-status-row">
								<span className="profile-status-chip">
									Member since {formatDate(profile.memberSince)}
								</span>
								<span className="profile-status-chip">
									Last seen {formatDate(profile.lastSeen)}
								</span>
								<span className="profile-status-chip">
									{profile.isOnline ? "Online now" : "Currently offline"}
								</span>
							</div>
						</div>
					</div>

					<div className="profile-stats-grid">
						<div className="profile-stat-card">
							<span className="profile-stat-label">Points</span>
							<strong className="profile-stat-value">
								{profile.points}
							</strong>
						</div>
						<div className="profile-stat-card">
							<span className="profile-stat-label">Tasks completed</span>
							<strong className="profile-stat-value">
								{completedTotal}
							</strong>
						</div>
						<div className="profile-stat-card">
							<span className="profile-stat-label">Average grade</span>
							<strong className="profile-stat-value">
								{averageSummary}
							</strong>
						</div>
					</div>
				</section>

				<section className="profile-grid">
					<article className="profile-panel box-light">
						<h2 className="profile-panel-title">Account details</h2>
						<div className="profile-detail-list">
							<div className="profile-detail-item">
								<span className="profile-detail-label">Email</span>
								<span className="profile-detail-value">
									{profile.email}
								</span>
							</div>
							<div className="profile-detail-item">
								<span className="profile-detail-label">Member since</span>
								<span className="profile-detail-value">
									{formatDate(profile.memberSince)}
								</span>
							</div>
							<div className="profile-detail-item">
								<span className="profile-detail-label">Last seen</span>
								<span className="profile-detail-value">
									{formatDate(profile.lastSeen)}
								</span>
							</div>
							<div className="profile-detail-item">
								<span className="profile-detail-label">Status</span>
								<span className="profile-detail-value">
									{profile.isOnline ? "online" : "offline"}
								</span>
							</div>
						</div>
					</article>

					<article className="profile-panel box-light">
						<h2 className="profile-panel-title">Tasks completed</h2>
						<div className="profile-breakdown-grid">
							<div className="profile-breakdown-card">
								<span className="profile-breakdown-label">Easy</span>
								<strong className="profile-breakdown-value">
									{profile.tasksCompleted.easy}
								</strong>
							</div>
							<div className="profile-breakdown-card">
								<span className="profile-breakdown-label">Medium</span>
								<strong className="profile-breakdown-value">
									{profile.tasksCompleted.medium}
								</strong>
							</div>
							<div className="profile-breakdown-card">
								<span className="profile-breakdown-label">Hard</span>
								<strong className="profile-breakdown-value">
									{profile.tasksCompleted.hard}
								</strong>
							</div>
						</div>
					</article>

					<article className="profile-panel box-light">
						<h2 className="profile-panel-title">Average grade</h2>
						<div className="profile-breakdown-grid">
							<div className="profile-breakdown-card">
								<span className="profile-breakdown-label">Easy</span>
								<strong className="profile-breakdown-value">
									{profile.averageGrade.easy}
								</strong>
							</div>
							<div className="profile-breakdown-card">
								<span className="profile-breakdown-label">Medium</span>
								<strong className="profile-breakdown-value">
									{profile.averageGrade.medium}
								</strong>
							</div>
							<div className="profile-breakdown-card">
								<span className="profile-breakdown-label">Hard</span>
								<strong className="profile-breakdown-value">
									{profile.averageGrade.hard}
								</strong>
							</div>
						</div>
					</article>
				</section>
			</div>
		</section>
	);
}
